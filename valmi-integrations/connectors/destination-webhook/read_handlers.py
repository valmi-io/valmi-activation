from proc_stdout_event_handlers import (
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
