#!env python
import json
import os
import sys
import subprocess
import io
from proc_stdout_handler import ProcStdoutHandlerThread
from handlers import (
    LogHandler,
    CheckpointHandler,
    RecordHandler,
    DefaultHandler,
    Engine,
    StoreWriter,
    StoreReader,
    StdoutWriter,
)


handlers = {
    "LOG": LogHandler,
    "CHECKPOINT": CheckpointHandler,
    "RECORD": RecordHandler,
    "default": DefaultHandler,
}


def main():
    entrypoint_str = os.environ["VALMI_ENTRYPOINT"]
    entrypoint = entrypoint_str.split(" ")

    # get the airbyte command
    airbyte_command = sys.argv[3]
    for i, arg in enumerate(sys.argv[1:]):
        if i >= len(entrypoint):
            airbyte_command = arg
            break

    if airbyte_command is None:
        sys.exit(5)

    engine = Engine()
    stdout_writer = StdoutWriter()
    store_writer = StoreWriter()

    # initialize handlers
    for key in handlers.keys():
        handlers[key] = handlers[key](engine=engine, store_writer=store_writer, stdout_writer=stdout_writer)

    if airbyte_command in ["spec", "check", "discover"]:
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

    elif airbyte_command in ["write"]:
        # TODO: read checkpoint from the engine

        run_id = engine.current_run_id()
        store_reader = StoreReader(run_id=run_id)
        # print(run_id)
        # print(sys.argv[1:])

        proc = subprocess.Popen(sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        proc_stdout_handler_thread = ProcStdoutHandlerThread(1, "ProcStdoutHandlerThread", engine, proc.stdout)
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

        proc.stdin.close()
        return_code = proc.poll()
        if return_code != 0:
            engine.error()
            sys.exit(return_code)

        proc_stdout_handler_thread.destroy()
        proc_stdout_handler_thread.join()

        sys.exit(0)


if __name__ == "__main__":
    main()
