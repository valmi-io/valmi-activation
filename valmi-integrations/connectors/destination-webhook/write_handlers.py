#!env python
import json
import os
from os.path import join
import time
import uuid
from pydantic import UUID4
import requests
from requests.adapters import HTTPAdapter, Retry

# TODO: Constants - need to become env vars
MAGIC_NUM = 0x7FFFFFFF
HTTP_TIMEOUT = 3  # seconds
MAX_HTTP_RETRIES = 3

## initalise requests session with retries
req_session = requests.Session()
# retry on all errors except 400 and 401
status_forcelist = tuple(x for x in requests.status_codes._codes if x > 400 and x not in [400, 401])
retries = Retry(total=MAX_HTTP_RETRIES, backoff_factor=0.1, status_forcelist=status_forcelist)
req_session.mount("http://", HTTPAdapter(max_retries=retries))


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

    def register_records(self, num_records):
        self.records_in_chunk = self.records_in_chunk + num_records
        self.total_records = self.total_records + num_records


class NullEngine:
    def __init__(self) -> None:
        self.connector_state = None
        pass

    def error(self):
        pass

    def success(self):
        pass

    def metric(self):
        pass

    def current_run_details(self):
        return {}

    def abort_required(self):
        return False


class Engine(NullEngine):
    def __init__(self, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)
        self.engine_url = os.environ["ACTIVATION_ENGINE_URL"]
        run_time_args = self.current_run_details()
        self.connector_state = ConnectorState(run_time_args=run_time_args)

    def current_run_details(self):
        sync_id = du(os.environ.get("DAGSTER_RUN_JOB_NAME", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
        r = req_session.get(f"{self.engine_url}/syncs/{sync_id}/runs/current_run_details", timeout=HTTP_TIMEOUT)
        return r.json()

    def metric(self):
        print("Sending metric")
        print(
            {
                "sync_id": self.connector_state.run_time_args["sync_id"],
                "run_id": self.connector_state.run_time_args["run_id"],
                "chunk_id": self.connector_state.num_chunks,
                "connector_id": "dest",
                "metrics": {"success": self.connector_state.records_in_chunk},
            }
        )
        r = req_session.post(
            f"{self.engine_url}/metrics/",
            timeout=HTTP_TIMEOUT,
            json={
                "sync_id": self.connector_state.run_time_args["sync_id"],
                "run_id": self.connector_state.run_time_args["run_id"],
                "chunk_id": self.connector_state.num_chunks,
                "connector_id": "dest",
                "metrics": {"success": self.connector_state.records_in_chunk},
            },
        )
        print(r.text)

    def error(self, msg="error"):
        # TODO: finish this
        print("sending error")
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = req_session.post(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/error/", timeout=HTTP_TIMEOUT, json={"error": msg}
        )
        print(r.text)

    def abort_required(self):
        return False
        # TODO: finish this
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = req_session.get(f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}", timeout=HTTP_TIMEOUT)
        return r.json()["abort_required"]

    def checkpoint(self, state):
        return
        # TODO: finish this
        print("sending checkpoint")
        sync_id = self.connector_state.run_time_args["sync_id"]
        run_id = self.connector_state.run_time_args["run_id"]
        r = req_session.post(
            f"{self.engine_url}/syncs/{sync_id}/runs/{run_id}/checkpoint/", timeout=HTTP_TIMEOUT, json=state
        )
        print(r.text)


class StoreWriter:
    def __init__(self) -> None:
        pass

    def store(self, record):
        print(record)


class StdoutWriter:
    def __init__(self) -> None:
        pass

    def store(self, record):
        print(record)


class StoreReader:
    def __init__(self, engine: NullEngine) -> None:
        self.engine = engine
        self.connector_state: ConnectorState = self.engine.connector_state
        store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
        if store_config["provider"] == "local":
            path_name = join(store_config["local"]["directory"], self.connector_state.run_time_args["run_id"])

            self.path_name = path_name
            self.last_handled_fn = None

    def read(self):
        while True:
            if not os.path.exists(self.path_name):
                time.sleep(1)
                yield ""
            list_dir = sorted([f.lower() for f in os.listdir(self.path_name)], key=lambda x: int(x[:-5]))
            for fn in list_dir:
                if self.last_handled_fn is not None and int(fn[:-5]) <= int(self.last_handled_fn[:-5]):
                    continue
                if fn.endswith(".vald"):
                    with open(join(self.path_name, fn), "r") as f:
                        for line in f.readlines():
                            # print("yiedling", line)
                            yield line

                    self.last_handled_fn = fn
                # print(fn)
                # print(f"magic num {MAGIC_NUM}")
                if fn.startswith(f"{MAGIC_NUM+1}"):
                    # print("returning")
                    return
            time.sleep(3)
            yield ""


class DefaultHandler:
    def __init__(
        self,
        engine: Engine = None,
        store_writer: StoreWriter = None,
        stdout_writer: StdoutWriter = None,
        store_reader: StoreReader = None,
    ) -> None:
        self.engine = engine
        self.store_writer = store_writer
        self.stdout_writer = stdout_writer
        self.store_reader = store_reader
        pass

    def handle(self, record) -> bool:
        print(json.dumps(record))
        return True


class LogHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(LogHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        return


class CheckpointHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(CheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        # TODO: Hack - use trace messages
        self.engine.connector_state.register_records(self.engine.connector_state.run_time_args["chunk_size"])
        self.engine.metric()
        self.engine.register_chunk()
        return True


class RecordHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(RecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        return True  # to continue reading


class TraceHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(CheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        print(json.dumps(record))
        # TODO: send engine error & kill proc
        # sys.exit(0)
