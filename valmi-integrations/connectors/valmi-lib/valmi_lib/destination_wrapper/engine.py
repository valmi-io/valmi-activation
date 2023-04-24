"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Friday, March 17th 2023, 8:50:50 pm
Author: Rajashekar Varkala @ valmi.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import copy
import os
import uuid
from pydantic import UUID4
import requests
from requests.adapters import HTTPAdapter, Retry

# TODO: Constants - need to come from current_run_details
HTTP_TIMEOUT = 3  # seconds
MAX_HTTP_RETRIES = 5
CONNECTOR_STRING = "dest"


# desanitise uuid
def du(uuid_str: str) -> UUID4:
    return uuid.UUID(uuid_str.replace("_", "-"))


class ConnectorState:
    def __init__(self, run_time_args=[]) -> None:
        self.num_chunks = run_time_args["chunk_id"]
        self.begin_records = self.num_chunks * run_time_args["chunk_size"]
        self.records_in_chunk = 0
        self.records_in_this_connector_intance = 0

        self.run_time_args = run_time_args

    def register_chunk(self):
        self.num_chunks = self.num_chunks + 1

    def total_records(self):
        return self.begin_records + self.records_in_this_connector_intance

    def register_records(self, num_records):
        self.records_in_this_connector_intance = num_records
        self.records_in_chunk = self.total_records() - (self.num_chunks * self.run_time_args["chunk_size"])


class NullEngine:
    def __init__(self) -> None:
        self.connector_state = None
        pass

    def error(self, msg="error"):
        pass

    def success(self):
        pass

    def metric(self):
        pass

    def metric_ext(self, metric_json, chunk_id, commit=False):
        pass

    def current_run_details(self):
        return {}

    def abort_required(self):
        return False


class Engine(NullEngine):
    def __init__(self, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)
        self.engine_url = os.environ["ACTIVATION_ENGINE_URL"]

        self.session_with_retries = requests.Session()
        # retry on all errors except 400 and 401
        status_forcelist = tuple(x for x in requests.status_codes._codes if x > 400 and x not in [400, 401])
        retries = Retry(total=MAX_HTTP_RETRIES, backoff_factor=5, status_forcelist=status_forcelist)
        self.session_with_retries.mount("http://", HTTPAdapter(max_retries=retries))
        self.session_with_retries.mount("https://", HTTPAdapter(max_retries=retries))

        self.session_without_retries = requests.Session()
        status_forcelist = []
        retries = Retry(total=0, backoff_factor=5, status_forcelist=status_forcelist)
        self.session_without_retries.mount("http://", HTTPAdapter(max_retries=retries))
        self.session_without_retries.mount("https://", HTTPAdapter(max_retries=retries))

        run_time_args = self.current_run_details()
        self.connector_state = ConnectorState(run_time_args=run_time_args)

    def current_run_details(self):
        sync_id = du(os.environ.get("DAGSTER_RUN_JOB_NAME", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
        r = self.session_with_retries.get(
            f"{self.engine_url}/syncs/{sync_id}/runs/current_run_details", timeout=HTTP_TIMEOUT
        )
        return r.json()

    def metric(self, commit=False):
        self.metric_ext({"success": self.connector_state.records_in_chunk}, commit=commit)

    def metric_ext(self, metric_json, chunk_id, commit=False):
        print("Sending metric")
        # TODO: remove the following code. just to make it visible in the UI for now
        metric_copy = copy.deepcopy(metric_json)
        keys_list = list(metric_copy.keys())
        for key in keys_list:
            if key in [
                "upsert",
                "append",
                "create",
                "update",
            ]:
                metric_copy["success"] = metric_copy[key]
                del metric_copy[key]

        payload = {
            "sync_id": self.connector_state.run_time_args["sync_id"],
            "run_id": self.connector_state.run_time_args["run_id"],
            "chunk_id": chunk_id,
            "connector_id": CONNECTOR_STRING,
            "metrics": metric_copy,
            "commit": commit,
        }

        print("payload ", payload)
        if commit:
            r = self.session_with_retries.post(
                f"{self.engine_url}/metrics/",
                timeout=HTTP_TIMEOUT,
                json=payload,
            )
            r.raise_for_status()
        else:
            try:
                r = self.session_without_retries.post(
                    f"{self.engine_url}/metrics/",
                    timeout=HTTP_TIMEOUT,
                    json=payload,
                )
            except Exception:
                pass

    def error(self, msg="error"):
        print("sending error ", msg)
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = self.session_with_retries.post(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/status/{CONNECTOR_STRING}/",
            timeout=HTTP_TIMEOUT,
            json={"status": "failed", "message": msg},
        )
        r.raise_for_status()

    def success(self):
        print("sending success ")
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = self.session_with_retries.post(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/status/{CONNECTOR_STRING}/",
            timeout=HTTP_TIMEOUT,
            json={"status": "success"},
        )
        r.raise_for_status()

    def abort_required(self):
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = self.session_with_retries.get(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/synchronize_connector_engine", timeout=HTTP_TIMEOUT
        )
        return r.json()["abort_required"]

    def checkpoint(self, state):
        print("sending checkpoint")
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = self.session_with_retries.post(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/state/{CONNECTOR_STRING}/",
            timeout=HTTP_TIMEOUT,
            json=state,
        )
        r.raise_for_status()
