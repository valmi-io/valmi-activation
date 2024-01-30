'''
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, August 23rd 2023, 1:40:48 pm
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


MAGIC_DELIM = ":zZ9Vy9:"  # short unique id to delimit the samples


class SampleRetrieverTask(object):

    def __init__(self, sync_id: str, run_id: str, collector: str, metric_type: str):
        self.sync_id = sync_id
        self.run_id = run_id
        self.collector = collector
        self.metric_type = metric_type

    def __call__(self):
        store_config = json.loads(v.get("VALMI_INTERMEDIATE_STORE"))
        storage = StorageFactory.get_storage(
            store_config,
            self.run_id,
            self.collector,
            self.metric_type)
        return storage.get_data()

    def __str__(self):
        return '%s %s %s %s' % (self.sync_id, self.run_id, self.collector, self.metric_type)


class Storage(object):
    def __init__(self, store_config: dict, run_id: str, collector: str, metric_type: str):
        self.store_config = store_config
        self.run_id = run_id
        self.collector = collector
        self.metric_type = metric_type

    @abstractmethod
    def get_data(self):
        pass


class StorageFactory(object):
    @staticmethod
    def get_storage(store_config: str, run_id: str, collector: str, metric_type: str) -> Storage:
        if store_config["provider"] == "local":
            return LocalStorage(store_config, run_id, collector, metric_type)
        else:
            raise Exception("Log provider not supported!")


class LocalStorage(Storage):
    def __init__(self, *args, **kwargs):
        super(LocalStorage, self).__init__(*args, **kwargs)

    def get_data(self):
        samples_file = join(self.store_config["local"]["directory"],
                            str(self.run_id),
                            "samples",
                            self.collector,
                            f"{self.metric_type}.vals")

        con = db.connect(':memory:')

        columns = [
            'rejection_code',
            'synthetic_internal_id',
            'data',
            'rejection_message',
            'rejection_metadata'
        ]
        dtypes = [
            'VARCHAR',
            'VARCHAR',
            'VARCHAR',
            'VARCHAR',
            'VARCHAR'
        ]
        con.execute(
            "SELECT * FROM read_csv('%s', sep='%s', columns = %s) ORDER BY rejection_code"
            % (samples_file, MAGIC_DELIM, {col:dtypes[i] for i, col in enumerate(columns)}))
        rows = con.fetchall()
        return {"rows": rows, "header": columns}


def main():
    from vyperconfig import setup_vyper
    setup_vyper()
    task = SampleRetrieverTask("sync_id", "f4bd1a4e-27ba-4347-a83a-8a7fc29b1141", "dest", "succeeded")
    print(task)
    print(task())


if __name__ == "__main__":
    main()
