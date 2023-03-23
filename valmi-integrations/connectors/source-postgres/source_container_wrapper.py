"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Friday, March 10th 2023, 8:49:37 pm
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

import json
import os
import sys
from os.path import join
import subprocess
import io
import uuid
from pydantic import UUID4
import requests
from requests.adapters import HTTPAdapter, Retry

# TODO: Constants - need to become env vars
MAGIC_NUM = 0x7FFFFFFF
HTTP_TIMEOUT = 3  # seconds
MAX_HTTP_RETRIES = 5
CONNECTOR_STRING = "src"


# desanitise uuid
def du(uuid_str: str) -> UUID4:
    return uuid.UUID(uuid_str.replace("_", "-"))


class ConnectorState:
    def __init__(self, run_time_args=[]) -> None:
        self.num_chunks = run_time_args["chunk_id"]
        self.records_in_chunk = 0
        self.total_records = self.num_chunks * run_time_args["chunk_size"]
        self.run_time_args = run_time_args

    def register_chunk(self):
        self.num_chunks = self.num_chunks + 1
        self.records_in_chunk = 0

    def register_record(self):
        self.records_in_chunk = self.records_in_chunk + 1
        self.total_records = self.total_records + 1


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

    def metric_ext(self, metric_json, commit=False):
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

    def metric_ext(self, metric_json, commit=False):
        print("Sending metric")
        payload = {
            "sync_id": self.connector_state.run_time_args["sync_id"],
            "run_id": self.connector_state.run_time_args["run_id"],
            "chunk_id": self.connector_state.num_chunks,
            "connector_id": CONNECTOR_STRING,
            "metrics": metric_json,
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
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = self.session_with_retries.post(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/state/{CONNECTOR_STRING}/",
            timeout=HTTP_TIMEOUT,
            json=state,
        )
        r.raise_for_status()


class NullWriter:
    def __init__(self, engine: NullEngine) -> None:
        pass

    def write(self, record, last=False):
        pass

    def flush(self, last=False):
        pass

    def finalize(self):
        pass


class StdoutWriter(NullWriter):
    pass


class StoreWriter(NullWriter):
    def __init__(self, engine: NullEngine) -> None:
        self.engine = engine
        self.connector_state: ConnectorState = self.engine.connector_state
        store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
        if store_config["provider"] == "local":
            path_name = join(store_config["local"]["directory"], self.connector_state.run_time_args["run_id"])
            os.makedirs(path_name, exist_ok=True)

            self.path_name = path_name
            self.records = []

    def write(self, record, last=False):
        self.records.append(record)
        self.connector_state.register_record()
        if self.connector_state.records_in_chunk >= self.connector_state.run_time_args["chunk_size"]:
            self.flush(last=False)
            self.records = []
            self.engine.metric(commit=True)
            self.connector_state.register_chunk()
        elif self.connector_state.records_in_chunk % self.connector_state.run_time_args["records_per_metric"] == 0:
            self.engine.metric(commit=False)

    def flush(self, last=False):
        # list_dir = sorted([f.lower() for f in os.listdir(self.path_name)], key=lambda x: int(x[:-5]))
        new_file_name = f"{MAGIC_NUM}.vald" if last else f"{self.engine.connector_state.num_chunks}.vald"
        with open(join(self.path_name, f"{int(new_file_name[:-5])+1}.vald"), "w") as f:
            for record in self.records:
                f.write(json.dumps(record))
                f.write("\n")

    def finalize(self):
        self.flush(last=True)
        self.engine.metric(commit=True)


class DefaultHandler:
    def __init__(
        self, engine: Engine = None, store_writer: StoreWriter = None, stdout_writer: StdoutWriter = None
    ) -> None:
        self.engine = engine
        self.store_writer = store_writer
        self.stdout_writer = stdout_writer
        pass

    def handle(self, record):
        print(json.dumps(record))

    def finalize(self):
        pass


class LogHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(LogHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        print(json.dumps(record))


class CheckpointHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(CheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        print(json.dumps(record))
        self.engine.checkpoint(record)


class RecordHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(RecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        self.store_writer.write(record)

    def finalize(self):
        self.store_writer.finalize()


class TraceHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(TraceHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        print(json.dumps(record))
        if record["trace"]["type"] == "ERROR":
            self.engine.error(record["trace"]["error"]["message"])
            sys.exit(0)
        elif record["trace"]["type"] == "ESTIMATE":
            self.engine.metric_ext(
                {record["trace"]["estimate"]["row_kind"]: record["trace"]["estimate"]["row_estimate"]}, commit=True
            )


handlers = {
    "LOG": LogHandler,
    "STATE": CheckpointHandler,
    "RECORD": RecordHandler,
    "default": DefaultHandler,
    "TRACE": TraceHandler,
}


def get_airbyte_command():
    entrypoint_str = os.environ["VALMI_ENTRYPOINT"]
    entrypoint = entrypoint_str.split(" ")

    airbyte_command = sys.argv[3]
    for i, arg in enumerate(sys.argv[1:]):
        if i >= len(entrypoint):
            airbyte_command = arg
            break

    return airbyte_command


def get_config_file_path():
    # TODO: do this better
    config_file_path = None
    for i, arg in enumerate(sys.argv):
        if arg == "--config":
            config_file_path = sys.argv[i + 1]
            break

    return config_file_path


def populate_run_time_args(airbyte_command, engine, config_file_path):
    if airbyte_command == "read":
        run_time_args = engine.current_run_details()

        with open(config_file_path, "r") as f:
            config = json.loads(f.read())

        with open(config_file_path, "w") as f:
            config["run_time_args"] = run_time_args
            f.write(json.dumps(config))


def sync_engine_for_error(proc: subprocess, engine: NullEngine):
    if engine.abort_required():
        proc.kill()
        sys.exit(0)  # Not this connector's fault


def main():
    airbyte_command = get_airbyte_command()
    config_file = get_config_file_path()

    if airbyte_command is None or (airbyte_command != "spec" and config_file is None):
        sys.exit(5)

    # if arg in read, write:
    # read checkpoint from the engine

    if airbyte_command == "read":
        engine = Engine()
        store_writer = StoreWriter(engine)
    else:
        engine = NullEngine()
        store_writer = NullWriter(engine)

    # populate run_time_args
    populate_run_time_args(airbyte_command, engine, config_file_path=config_file)

    stdout_writer = StdoutWriter(engine)

    # initialize handlers
    for key in handlers.keys():
        handlers[key] = handlers[key](engine=engine, store_writer=store_writer, stdout_writer=stdout_writer)

    # create the subprocess
    proc = subprocess.Popen(
        sys.argv[1:],
        stdout=subprocess.PIPE,
    )

    # check engine errors every CHUNK_SIZE records
    record_types = handlers.keys()
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        if line.strip() == "":
            continue
        # print(line)
        json_record = json.loads(line)
        if json_record["type"] not in record_types:
            handlers["default"].handle(json_record)
        else:
            handlers[json_record["type"]].handle(json_record)

        # sync with engine for any errors - in the future -> to apply backpressure to the connector
        if airbyte_command == "read":
            if engine.connector_state.records_in_chunk % engine.connector_state.run_time_args["chunk_size"] == 0:
                sync_engine_for_error(proc, engine=engine)

    return_code = proc.poll()
    if return_code is not None and return_code != 0:
        engine.error("Connector exited with non-zero return code")
        sys.exit(return_code)
    else:
        if airbyte_command == "read":
            store_writer.finalize()
        engine.success()


if __name__ == "__main__":
    main()
