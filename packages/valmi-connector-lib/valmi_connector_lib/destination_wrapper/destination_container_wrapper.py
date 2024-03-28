"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Sunday, March 12th 2023, 8:43:08 pm
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
import subprocess
import io
from typing import Any, Dict

from valmi_connector_lib.common.logs import SingletonLogWriter, TimeAndChunkEndFlushPolicy
from valmi_connector_lib.common.samples import SampleWriter
from valmi_connector_lib.destination_wrapper.engine import CONNECTOR_STRING

from .proc_stdout_handler import ProcStdoutHandlerThread
from .proc_stdout_event_handlers import (
    Engine,
    StoreReader,
    NullEngine,
)
from .read_handlers import ReadCheckpointHandler, ReadDefaultHandler, ReadLogHandler, ReadRecordHandler
from .proc_stdout_handler import handlers as stdout_handlers

handlers = {
    "LOG": ReadLogHandler,
    "STATE": ReadCheckpointHandler,
    "RECORD": ReadRecordHandler,
    "default": ReadDefaultHandler,
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
    if airbyte_command == "write":
        run_time_args = engine.current_run_details()

        with open(config_file_path, "r") as f:
            config = json.loads(f.read())

        with open(config_file_path, "w") as f:
            config["run_time_args"] = run_time_args
            f.write(json.dumps(config))

        if 'state' in run_time_args:
            # create a new state file alongside the config file
            state_file_path = os.path.join(os.path.dirname(config_file_path), 'state.json')
            set_state_file_path(state_file_path)
            set_loaded_state(run_time_args['state'])
            with open(state_file_path, "w") as f:
                f.write(json.dumps(run_time_args['state']))


state_file_path = None
loaded_state = None


def set_state_file_path(file_path: str):
    global state_file_path
    state_file_path = file_path


def set_loaded_state(state: Dict[str, Any]):
    global loaded_state
    loaded_state = state


def is_state_available():
    global state_file_path
    return state_file_path is not None


def main():
    airbyte_command = get_airbyte_command()
    config_file = get_config_file_path()

    if airbyte_command is None or (airbyte_command != "spec" and config_file is None):
        sys.exit(5)

    # if arg in read, write:
    # read checkpoint from the engine

    if airbyte_command == "write":
        engine = Engine()
    else:
        engine = NullEngine()

    # populate run_time_args
    populate_run_time_args(airbyte_command, engine, config_file_path=config_file)

    if airbyte_command in ["spec", "check", "discover", "create"]:
        # initialize handlers
        for key in stdout_handlers.keys():
            stdout_handlers[key] = stdout_handlers[key](engine=engine, store_writer=None, stdout_writer=None)

        # create the subprocess
        subprocess_args = sys.argv[1:]
        proc = subprocess.Popen(
            subprocess_args,
            stdout=subprocess.PIPE,
        )

        record_types = handlers.keys()
        for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
            if line.strip() == "":
                continue
            json_record = json.loads(line)
            if json_record["type"] not in record_types:
                stdout_handlers["default"].handle(json_record)
            else:
                stdout_handlers[json_record["type"]].handle(json_record)

        return_code = proc.poll()
        if return_code is not None and return_code != 0:
            engine.error("Process exited with non-zero return code. %s" % return_code)
            sys.exit(return_code)

    elif airbyte_command in ["write"]:
        # initialize LogWriter
        SingletonLogWriter(os.environ["VALMI_INTERMEDIATE_STORE"],
                           TimeAndChunkEndFlushPolicy(os.environ["VALMI_INTERMEDIATE_STORE"]),
                           engine.connector_state.run_time_args["sync_id"],
                           engine.connector_state.run_time_args["run_id"],
                           CONNECTOR_STRING)
       
        # initialize SampleWriter
        SampleWriter.get_writer_by_metric_type(store_config_str=os.environ["VALMI_INTERMEDIATE_STORE"],
                                               sync_id=engine.connector_state.run_time_args["sync_id"],
                                               run_id=engine.connector_state.run_time_args["run_id"],
                                               connector=CONNECTOR_STRING)

        # initialize handler
        for key in handlers.keys():
            handlers[key] = handlers[key](engine=engine, store_writer=None, stdout_writer=None)

        global loaded_state
        store_reader = StoreReader(engine=engine, state=loaded_state)

        # create the subprocess
        subprocess_args = sys.argv[1:]
        if is_state_available():
            subprocess_args.append("--state")
            subprocess_args.append(state_file_path)
        proc = subprocess.Popen(subprocess_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        try:
            proc_stdout_handler_thread = ProcStdoutHandlerThread(
                1, "ProcStdoutHandlerThread", engine, proc, proc.stdout
            )
            proc_stdout_handler_thread.start()

            record_types = handlers.keys()

            for line in store_reader.read():
                if line.strip() == "":
                    continue
                json_record = json.loads(line)
                if json_record["type"] not in record_types:
                    if not handlers["default"].handle(json_record):
                        break
                else:
                    if not handlers[json_record["type"]].handle(json_record):
                        break
                proc.stdin.write(line.encode("utf-8"))

        except Exception as e:
            engine.error(msg=str(e))
            proc.stdin.close()
            proc.kill()
            proc_stdout_handler_thread.destroy()
            proc_stdout_handler_thread.join()
            raise
        else:
            proc.stdin.close()
            return_code = proc.poll()
            if return_code is not None and return_code != 0:
                engine.error("Process exited with non-zero return code. %s" % return_code)
                sys.exit(return_code)

            proc_stdout_handler_thread.destroy()
            proc_stdout_handler_thread.join()
            engine.success()


if __name__ == "__main__":
    main()
