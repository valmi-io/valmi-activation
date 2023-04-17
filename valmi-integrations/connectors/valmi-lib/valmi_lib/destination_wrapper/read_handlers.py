"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Friday, March 17th 2023, 8:16:01 pm
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

from .proc_stdout_event_handlers import (
    Engine,
    StoreWriter,
    StoreReader,
    StdoutWriter,
)


class ReadDefaultHandler:
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
        return True


class ReadLogHandler(ReadDefaultHandler):
    def __init__(self, *args, **kwargs):
        super(ReadLogHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        return True


class ReadCheckpointHandler(ReadDefaultHandler):
    def __init__(self, *args, **kwargs):
        super(ReadCheckpointHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        # do an engine call to proceed.
        return True


class ReadRecordHandler(ReadDefaultHandler):
    def __init__(self, *args, **kwargs):
        super(ReadRecordHandler, self).__init__(*args, **kwargs)

    def handle(self, record) -> bool:
        return True  # to continue reading
