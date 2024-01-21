'''
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, August 17th 2023, 1:51:40 pm
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
'''

from abc import abstractmethod
from vyper import v
from os.path import join
import os
import sys
import json
import duckdb as db


MAGIC_DELIM = ":zZ9Vy9:"  # short unique id to delimit the log lines


class LogRetrieverTask(object):

    '''
    Only one log file is returned at the moment.
    While writing the log file, We will make sure there are enough new lines in the file.
    Only one of Since and Before is supported at the moment. If both are provided, Since is used.
    '''

    def __init__(self, sync_id: str, run_id: str, collector: str, before: int, since: int):
        self.sync_id = sync_id
        self.run_id = run_id
        self.collector = collector
        self.before = before  # exclusive
        self.since = since  # inclusive

    def __call__(self):
        store_config = json.loads(v.get("VALMI_INTERMEDIATE_STORE"))
        '''
        #  TESTING
        store_config['local']['directory'] = "/workspace/test_data/logs/runs/"
        #  TESTING
        '''
        storage = StorageFactory.get_storage(
            store_config,
            self.run_id, self.collector, self.before, self.since)
        files, meta = storage.list_files()

        # There is a possibility with this scheme that we might return the same line twice,
        # so make sure while writing the log file, flush the log files with the same timestamp.
        # Think a better and simple scheme if possible.
        # When asking for the next set of logs, look at meta and request with (since+1) timestamp,
        # and the before query with 'since' timestamp returned in the meta.
        return storage.get_data(files, meta)

    def __str__(self):
        return '%s %s %s %s %s' % (self.sync_id, self.run_id, self.collector, self.before, self.since)


class Storage(object):
    def __init__(self, store_config: dict, run_id: str, collector: str, before: int, since: int):
        self.store_config = store_config
        self.run_id = run_id
        self.collector = collector
        self.before = before
        self.since = since

    @abstractmethod
    def list_files(self):
        pass

    @abstractmethod
    def get_data(self, files_list, meta):
        pass


class StorageFactory(object):
    @staticmethod
    def get_storage(store_config: str, run_id: str, collector: str, before: int, since: int) -> Storage:
        if store_config["provider"] == "local":
            return LocalStorage(store_config, run_id, collector, before, since)
        else:
            raise Exception("Log provider not supported!")


class LocalStorage(Storage):
    def __init__(self, *args, **kwargs):
        super(LocalStorage, self).__init__(*args, **kwargs)

    def sort(self, files_list):
        return files_list

    def filter(self, files_list):
        return files_list

    def interval_test(self, interval):
        if self.since is not None:
            if interval[0] <= self.since and interval[1] > self.since:
                return True
        elif self.before is not None:
            if interval[0] < self.before and interval[1] >= self.before:
                return True
        return False

    def list_files(self):
        if self.since is None and self.before is None:
            return []

        dir_name = join(self.store_config["local"]["directory"], str(self.run_id), "logs", self.collector)
        list_dir = sorted([f.lower() for f in os.listdir(dir_name) if f.endswith('.vall')], key=lambda x: int(x[:-5]))

        filtered_list = []
        last_file_name = None

        file_start_ts = None
        next_file_start_ts = None

        spruced_list = list_dir + ["%s.vall" % sys.maxsize]
        for counter, fn in enumerate(spruced_list):
            if counter == 0:
                interval = (-1, int(fn[:-5]))
            else:
                interval = (int(last_file_name[:-5]), int(fn[:-5]))

            if self.interval_test(interval=interval):
                if counter == 0:
                    file_to_read = None
                else:
                    file_to_read = last_file_name
                    file_start_ts = file_to_read[:-5]
                if counter != len(spruced_list) - 1:
                    next_file_start_ts = spruced_list[counter][:-5]
                if file_to_read is not None:
                    filtered_list.append(join(dir_name, file_to_read))
                break
            last_file_name = fn
        return (filtered_list, {"since": file_start_ts, "before": next_file_start_ts})

    def get_data(self, files_list, meta):
        if len(files_list) <= 0:
            return {"meta": meta,
                    "logs": []}

        con = db.connect(':memory:')
        time_filter = ""
        if self.since is not None:
            time_filter = "WHERE timestamp_micros >= %s" % self.since
        elif self.before is not None:
            time_filter = "WHERE timestamp_micros < %s" % self.before
        con.execute(
            "SELECT * FROM read_csv(%s, sep='%s', columns={'timestamp_micros': 'BIGINT', 'message': 'VARCHAR'}) \
            %s \
            ORDER BY timestamp_micros ASC"
            % (files_list, MAGIC_DELIM, time_filter))
        '''
        con.execute(
            "SELECT * FROM read_csv(%s, sep='%s', columns={'timestamp_micros': 'BIGINT', 'message': 'VARCHAR'}) \
            \
            ORDER BY timestamp_micros ASC"
            % (files_list, MAGIC_DELIM))
        '''
        logs = con.fetchall()
        return {"meta": meta, "logs": logs}


def main():
    from vyperconfig import setup_vyper
    setup_vyper()
    task = LogRetrieverTask("sync_id", "f4bd1a4e-27ba-4347-a83a-8a7fc29b1141", "dest", 1, None)
    print(task)
    print(task())


if __name__ == "__main__":
    main()
