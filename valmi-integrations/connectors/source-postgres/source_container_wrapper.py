#!env python
import json
import os
import sys
from os.path import join
import subprocess
import io
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
        sync_id = du(os.environ.get("DAGSTER_RUN_JOB_NAME", "dummy"))
        r = requests.get(f"{ACTIVATION_ENGINE_URL}/syncs/{sync_id}/runs/current_run_id", timeout=HTTP_TIMEOUT)
        return r.json()["lastRunId"]


class StdoutWriter:
    def __init__(self) -> None:
        pass

    def store(self, record):
        print(record)


class StoreWriter:
    def __init__(self, run_id) -> None:
        store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
        if store_config["provider"] == "local":
            path_name = join(store_config["local"]["directory"], run_id)
            os.makedirs(path_name, exist_ok=True)

            self.path_name = path_name
            self.records = []
            self.counter = 0

    def write(self, record, last=False):
        self.counter = self.counter + 1
        self.records.append(record)
        if self.counter >= BUFFER_SIZE:
            self.flush(last=False)
            self.records = []
            self.counter = 0

    def flush(self, last=False):
        list_dir = sorted([f.lower() for f in os.listdir(self.path_name)], key=lambda x: int(x[:-5]))
        new_file_name = f"{MAGIC_NUM}.vald" if last else (list_dir[-1] if len(list_dir) > 0 else "0.vald")
        with open(join(self.path_name, f"{int(new_file_name[:-5])+1}.vald"), "w") as f:
            for record in self.records:
                f.write(json.dumps(record))

    def finalize(self):
        self.flush(last=True)


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


class RecordHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(RecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        self.store_writer.write(record)

    def finalize(self):
        self.store_writer.finalize()


handlers = {
    "LOG": LogHandler,
    "CHECKPOINT": CheckpointHandler,
    "RECORD": RecordHandler,
    "default": DefaultHandler,
}


def main():
    entrypoint_str = os.environ["VALMI_ENTRYPOINT"]
    entrypoint = entrypoint_str.split(" ")

    airbyte_command = sys.argv[3]
    for i, arg in enumerate(sys.argv[1:]):
        if i >= len(entrypoint):
            airbyte_command = arg
            break

    if airbyte_command is None:
        sys.exit(5)

    # if arg in read, write:
    # read checkpoint from the engine

    # store writer
    engine = Engine()
    run_id = engine.current_run_id()

    store_writer = StoreWriter(run_id=run_id)
    stdout_writer = StdoutWriter()

    # initialize handlers
    for key in handlers.keys():
        handlers[key] = handlers[key](engine=engine, store_writer=store_writer, stdout_writer=stdout_writer)

    # create the subprocess
    proc = subprocess.Popen(
        sys.argv[1:],
        stdout=subprocess.PIPE,
    )

    record_types = handlers.keys()
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        if line.strip() == "":
            continue
        json_record = json.loads(line)
        if json_record["type"] not in record_types:
            handlers["default"].handle(json_record)
        else:
            handlers[json_record["type"]].handle(json_record)

    return_code = proc.poll()
    if return_code != 0:
        engine.error()
        sys.exit(return_code)
    else:
        if airbyte_command not in ["spec", "check", "discover"]:
            store_writer.finalize()
        engine.success()


if __name__ == "__main__":
    main()
