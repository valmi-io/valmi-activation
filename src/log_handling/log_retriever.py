import time


class LogRetrieverTask(object):
    def __init__(self, sync_id: str, run_id: str, collector: str, before: int, after: int):
        self.sync_id = sync_id
        self.run_id = run_id
        self.collector = collector
        self.before = before
        self.after = after

    def __call__(self):
        time.sleep(5)  # pretend to take some time to do the work
        return '%s %s %s %s %s' % (self.sync_id, self.run_id, self.collector, self.before, self.after)

    def __str__(self):
        return '%s %s %s %s %s' % (self.sync_id, self.run_id, self.collector, self.before, self.after)
