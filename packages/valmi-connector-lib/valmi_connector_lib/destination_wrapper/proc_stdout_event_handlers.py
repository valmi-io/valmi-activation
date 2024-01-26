"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Monday, March 13th 2023, 9:59:01 am
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
from os.path import join
import time

from valmi_connector_lib.common.logs import SingletonLogWriter
from valmi_connector_lib.common.samples import SampleWriter

from .engine import NullEngine, ConnectorState, Engine

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
    def __init__(self, engine: NullEngine, state: str) -> None:
        self.engine = engine
        self.connector_state: ConnectorState = self.engine.connector_state
        self.loaded_state = state

        store_config = json.loads(os.environ["VALMI_INTERMEDIATE_STORE"])
        if store_config["provider"] == "local":
            path_name = join(store_config["local"]["directory"], self.connector_state.run_time_args["run_id"], "data")
            os.makedirs(path_name, exist_ok=True)
            self.path_name = path_name
            self.last_handled_fn = self.get_file_name_from_chunk_id(self.read_chunk_id_checkpoint())

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
                if fn.startswith(f"{MAGIC_NUM}"):
                    # print("returning")
                    return

                # Check for abort condition after reading a file
                if self.engine.abort_required():
                    return
                
            # Check for abort condition after exhausting files in the folder
            if self.engine.abort_required():
                return
            time.sleep(3)
            yield ""

    def read_chunk_id_checkpoint(self):
        # TODO: connector_state is not being used for destination, clean it up.
        if self.loaded_state is not None \
                and 'state' in self.loaded_state \
                and 'data' in self.loaded_state['state'] \
                and 'chunk_id' in self.loaded_state['state']['data']:
            return self.loaded_state['state']['data']['chunk_id']
        return None

    def get_file_name_from_chunk_id(self, chunk_id):
        if chunk_id is not None:
            return f"{chunk_id}.vald"
        return None


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
        if SingletonLogWriter.instance() is not None:
            SingletonLogWriter.instance().check_for_flush()
        return True


class LogHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(LogHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        log_str = json.dumps(record)
        print(log_str)
        if SingletonLogWriter.instance() is not None:
            SingletonLogWriter.instance().write(log_str)
        return


class CheckpointHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(CheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        print("Checkpoint seen")
        print(record)

        records_delivered = record["state"]["data"]["records_delivered"]
        finished = record["state"]["data"]["finished"]
        commit_state = record["state"]["data"]["commit_state"]
        commit_metric = record["state"]["data"]["commit_metric"]

        total_records = 0
        for k, v in records_delivered.items():
            total_records += v

        self.engine.connector_state.register_records(total_records)

        if commit_metric:
            self.engine.metric_ext(records_delivered, record["state"]["data"]["chunk_id"], commit=True)
            # self.engine.connector_state.register_chunk()
        if commit_state:
            self.engine.checkpoint(record)
            if SingletonLogWriter.instance() is not None:
                SingletonLogWriter.instance().data_chunk_flush_callback()
            SampleWriter.data_chunk_flush_callback()
        else:
            if SingletonLogWriter.instance() is not None:
                SingletonLogWriter.instance().check_for_flush()

        return True


class RecordHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(RecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        if SingletonLogWriter.instance() is not None:
            SingletonLogWriter.instance().check_for_flush()

        sample_writer = SampleWriter.get_writer_by_metric_type(metric_type=record["record"]["metric_type"])
        sample_writer.write(record)
        return True  # to continue reading


class TraceHandler(DefaultHandler):
    def __init__(self, *args, **kwargs):
        super(TraceHandler, self).__init__(*args, **kwargs)

    def handle(self, record):
        print(json.dumps(record))
        if SingletonLogWriter.instance() is not None:
            SingletonLogWriter.instance().check_for_flush()
        self.engine.error(record["trace"]["error"]["message"])
        return False
