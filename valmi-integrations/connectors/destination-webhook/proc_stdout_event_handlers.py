#!env python
import json
import os
from os.path import join
import time
from engine import NullEngine, ConnectorState, Engine

# TODO: Constants - need to become env vars
MAGIC_NUM = 0x7FFFFFFF


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
            if self.engine.abort_required():
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
        return


class CheckpointHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(CheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        print("Checkpoint seen")
        print(record)

        records_delivered = record["state"]["data"]["records_delivered"]
        finished = record["state"]["data"]["finished"]
        self.engine.connector_state.register_records(records_delivered)

        commit = False
        if finished or records_delivered % self.engine.connector_state.run_time_args["chunk_size"] == 0:
            commit = True
        if commit:
            self.engine.metric(commit=True)
            self.engine.connector_state.register_chunk()
            self.engine.checkpoint(record)
        else:
            self.engine.metric(commit=False)

        return True


class RecordHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(RecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        return True  # to continue reading


class TraceHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(TraceHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        print(json.dumps(record))
        self.engine.error(record["trace"]["error"]["message"])
        return False
