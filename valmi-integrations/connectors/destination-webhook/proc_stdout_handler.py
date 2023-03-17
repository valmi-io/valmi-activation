#!env python
import json
import os
import io
import threading
from write_handlers import LogHandler, CheckpointHandler, DefaultHandler, Engine, TraceHandler
import logging

handlers = {
    "LOG": LogHandler,
    "CHECKPOINT": CheckpointHandler,
    "default": DefaultHandler,
    "TRACE": TraceHandler,
}


class ProcStdoutHandlerThread(threading.Thread):
    def __init__(self, threadID: int, name: str, engine: Engine, proc_stdout) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name
        self.proc_stdout = proc_stdout
        self.engine = engine

    def run(self) -> None:
        # initialise handlers
        for key in handlers.keys():
            handlers[key] = handlers[key](engine=self.engine, store_writer=None, stdout_writer=None)

        while not self.exitFlag:
            try:
                record_types = handlers.keys()
                for line in io.TextIOWrapper(self.proc_stdout, encoding="utf-8"):
                    if line.strip() == "":
                        continue
                    print(line)
                    json_record = json.loads(line)
                    if json_record["type"] not in record_types:
                        handlers["default"].handle(json_record)
                    else:
                        handlers[json_record["type"]].handle(json_record)

                # stdout finished. clean close
                self.exitFlag = True
            except Exception as e:
                logging.exception(e)
                # panic
                print("Panicking ", str(e))
                self.engine.error(msg=str(e))
                os._exit(1)

    def destroy(self) -> None:
        self.exitFlag = True

    """
    def read_with_timeout(self, fd, timeout__s):
        buf = []
        e = epoll()
        e.register(fd, EPOLLIN)
        while True:
            ret = e.poll(timeout__s)
            if not ret or ret[0][1] is not EPOLLIN:
                break
            buf.append(fd.read(1))
        return "".join(buf)
    """
