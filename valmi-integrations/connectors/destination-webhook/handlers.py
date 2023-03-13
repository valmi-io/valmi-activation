#!env python
import json
import os
from os.path import join
import time
import uuid
from pydantic import UUID4
import requests

BUFFER_SIZE = 2
MAGIC_NUM = 0x7FFFFFFF

ACTIVATION_ENGINE_URL = "http://host.docker.internal:8000"
HTTP_TIMEOUT = 3


# desanitise uuid
def du(uuid_str: str) -> UUID4:
    return uuid.UUID(uuid_str.replace("_", "-"))


class Engine:
    def __init__(self) -> None:
        pass

    def error(self):
        pass

    def success(self):
        pass

    def metric(self):
        pass

    def current_run_id(self):
        sync_id = du(os.environ.get("DAGSTER_RUN_JOB_NAME", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
        r = requests.get(f"{ACTIVATION_ENGINE_URL}/syncs/{sync_id}/runs/current_run_id", timeout=HTTP_TIMEOUT)
        return r.json()["lastRunId"]


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
    def __init__(self, run_id) -> None:
        store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
        if store_config["provider"] == "local":
            path_name = join(store_config["local"]["directory"], run_id)

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
        print(json.dumps(record))


class CheckpointHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(CheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        print(json.dumps(record))  # do an engine call to proceed.


class RecordHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(RecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        return True  # to continue reading
