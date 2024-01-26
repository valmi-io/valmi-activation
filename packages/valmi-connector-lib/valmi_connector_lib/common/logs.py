'''
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Monday, August 21st 2023, 3:23:12 pm
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
import json
from os.path import join
import time
import os
from .constants import MAGIC_DELIM


class LogWriter:

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, store_config_str, flush_policy, sync_id, run_id, connector):
        self.flush_policy = flush_policy
        self.store_config = json.loads(store_config_str)
        self.lines = []
        self.sync_id = sync_id
        self.run_id = run_id
        self.connector = connector

    def reset(self):
        self.lines.clear()
        self.flush_policy.reset()

    def check_for_flush(self):
        if self.flush_policy.roll_over_file_required():
            self.flush()
            self.reset()

        elif self.flush_policy.flush_required():
            self.flush()

    def write(self, log_record):
        current_time = self.flush_policy.newline(log_record)
        self.lines.append((current_time, log_record))

        self.check_for_flush()

    def flush(self):
        if len(self.lines) > 0:
            # TODO: do cloud push for aws, s3 when we do k8s
            file_path = join(self.store_config['local']['directory'],
                             self.run_id, "logs", self.connector, self.flush_policy.get_current_file_name())
            dir_name = os.path.dirname(file_path)
            os.makedirs(dir_name, exist_ok=True)
            with open(file_path, "w") as f:
                for line in self.lines:
                    f.write(f"{line[0]}")
                    f.write(MAGIC_DELIM)
                    f.write(line[1])
                    f.write("\n")

    def data_chunk_flush_callback(self):
        self.flush_policy.set_data_chunk_flushed()
        self.check_for_flush()


class FlushPolicy:
    def __init__(self, store_config_str: str):
        self.store_config = json.loads(store_config_str)

    @abstractmethod
    def flush_required(self):
        pass

    @abstractmethod
    def newline(self, log_record):
        pass

    @abstractmethod
    def roll_over_file_required(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def get_current_file_name(self):
        pass


class TimeAndChunkEndFlushPolicy(FlushPolicy):
    def __init__(self, *args, **kwargs):
        super(TimeAndChunkEndFlushPolicy, self).__init__(*args, **kwargs)
        self.reset()

    def flush_required(self):
        if (self.first_line_time is not None
                and self.timestamp_changed
                and self.last_line_time - self.first_line_time > self.store_config['local']['log_flush_interval'] * 1000000) \
                or self.data_chunk_flushed:
            return True
        return False
    
    def roll_over_file_required(self):
        if (self.num_lines >= self.store_config['local']['max_lines_per_file_hint']):
            return True
        return False

    def newline(self, log_record):
        self.num_lines += 1
        current_time = int(time.time() * 1000000)  # microseconds
        if self.first_line_time is None:
            self.first_line_time = current_time

        if self.last_line_time is not None and current_time != self.last_line_time:
            self.timestamp_changed = True
        else:
            self.timestamp_changed = False

        self.last_line_time = current_time
        return current_time

    def set_data_chunk_flushed(self):
        self.data_chunk_flushed = True

    def reset(self):
        self.first_line_time = None
        self.last_line_time = None
        self.timestamp_changed = False
        self.data_chunk_flushed = False
        self.num_lines = 0

    def get_current_file_name(self):
        return f"{self.first_line_time}.vall"


class SingletonLogWriter(LogWriter):
    __initialized = False

    def __new__(cls, *args, **kwargs) -> object:
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingletonLogWriter, cls).__new__(cls, args, kwargs)
        return cls._instance

    def __init__(self, store_config, flush_policy, sync_id, run_id, connector):
        if SingletonLogWriter.__initialized:
            return

        SingletonLogWriter.__initialized = True
        super(SingletonLogWriter, self).__init__(store_config, flush_policy, sync_id, run_id, connector)

    @classmethod
    def instance(cls):
        if hasattr(cls, "_instance"):
            return cls._instance
        return None


def main():
    store_config_str = "{\"provider\": \"local\", \"local\": {\"directory\": \"/tmp/shared_dir/test_logs\", \"max_lines_per_file_hint\" : 100, \"log_flush_interval\": 5}}"
    SingletonLogWriter(store_config_str, TimeAndChunkEndFlushPolicy(store_config_str=store_config_str), "sync_id", "run_id", "connector")

    for i in range(100000):
        SingletonLogWriter.instance().write("line %d" % i)
        time.sleep(0.1)


if __name__ == "__main__":
    main()