"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Monday, March 13th 2023, 9:56:23 am
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
import io
import threading
from .proc_stdout_event_handlers import LogHandler, CheckpointHandler, DefaultHandler, Engine, TraceHandler
import logging

handlers = {
    "LOG": LogHandler,
    "STATE": CheckpointHandler,
    "default": DefaultHandler,
    "TRACE": TraceHandler,
}


class ProcStdoutHandlerThread(threading.Thread):
    def __init__(self, thread_id: int, name: str, engine: Engine, proc, proc_stdout) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.exit_flag = False
        self.name = name
        self.proc_stdout = proc_stdout
        self.engine = engine
        self.proc = proc

    def run(self) -> None:
        # initialise handlers
        for key in handlers.keys():
            handlers[key] = handlers[key](engine=self.engine, store_writer=None, stdout_writer=None)

        while not self.exit_flag:
            try:
                record_types = handlers.keys()
                for line in io.TextIOWrapper(self.proc_stdout, encoding="utf-8"):
                    if line.strip() == "":
                        continue
                    print(line)
                    json_record = json.loads(line)

                    # We want to check abort status after every chunk,
                    # STATE record is written after every chunk
                    if json_record["type"] == "STATE":
                        if self.engine.abort_required():
                            self.proc.kill()
                            os._exit(0)

                    if json_record["type"] not in record_types:
                        handlers["default"].handle(json_record)
                    else:
                        ret_val = handlers[json_record["type"]].handle(json_record)
                        if ret_val is False:  # TODO: comes from ERROR Trace, should be handled cleanly
                            self.proc.kill()
                            os._exit(0)  # error is already logged with engine in the handler

                # stdout finished. clean close
                self.exit_flag = True
            except Exception as e:
                logging.exception(e)
                # panic
                print("Panicking ", str(e))
                self.engine.error(msg=str(e))
                os._exit(1)

    def destroy(self) -> None:
        self.exit_flag = True

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
