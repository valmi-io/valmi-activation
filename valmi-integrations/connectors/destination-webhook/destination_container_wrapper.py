#!env python
import json
import os
import sys
import subprocess
import io
from proc_stdout_handler import ProcStdoutHandlerThread
from write_handlers import (
    Engine,
    StoreReader,
    NullEngine,
)
from read_handlers import ReadCheckpointHandler, ReadDefaultHandler, ReadLogHandler, ReadRecordHandler


handlers = {
    "LOG": ReadLogHandler,
    "CHECKPOINT": ReadCheckpointHandler,
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


def main():
    airbyte_command = get_airbyte_command()
    config_file = get_config_file_path()

    if airbyte_command is None or config_file is None:
        sys.exit(5)

    # if arg in read, write:
    # read checkpoint from the engine

    if airbyte_command == "write":
        engine = Engine()
    else:
        engine = NullEngine()

    # populate run_time_args
    populate_run_time_args(airbyte_command, engine, config_file_path=config_file)

    # initialize handlers
    for key in handlers.keys():
        handlers[key] = handlers[key](engine=engine, store_writer=None, stdout_writer=None)

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

        store_reader = StoreReader(engine=engine)

        proc = subprocess.Popen(sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        try:
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

        except Exception:
            engine.error()
            raise
        finally:
            proc.stdin.close()
            return_code = proc.poll()
            if return_code != 0:
                engine.error()
                sys.exit(return_code)

            proc_stdout_handler_thread.destroy()
            proc_stdout_handler_thread.join()


if __name__ == "__main__":
    main()
