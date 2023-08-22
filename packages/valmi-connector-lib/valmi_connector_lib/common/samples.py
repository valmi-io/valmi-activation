from abc import abstractmethod
import json
from os.path import join
import time
import os
from typing import List
from airbyte_cdk.models import (
    AirbyteMessage,
    Type
)
from uuid import uuid4

MAGIC_DELIM = ":zZ9Vy9:"


class SampleWriter:
    writers = {}

    @classmethod
    def get_writer_by_metric_type(cls, store_config_str, sync_id, run_id, connector, metric_type):
        if metric_type not in SampleWriter.writers or SampleWriter.writers[metric_type] is None:
            SampleWriter.writers[metric_type] = SampleWriter(store_config_str,
                                                             ChunkEndFlushPolicy(store_config_str=store_config_str),
                                                             sync_id,
                                                             run_id,
                                                             connector,
                                                             metric_type)
        return SampleWriter.writers[metric_type]

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, store_config_str, flush_policy, sync_id, run_id, connector, metric_type):
        self.flush_policy = flush_policy
        self.store_config = json.loads(store_config_str)
        self.records: List[AirbyteMessage] = []
        self.sync_id = sync_id
        self.run_id = run_id
        self.connector = connector
        self.metric_type = metric_type

    def reset(self):
        self.records.clear()
        self.flush_policy.reset()

    def check_for_flush(self):
        if self.flush_policy.flush_required():
            self.flush()
            self.reset()

    def write(self, json_log_record):
        # TODO: Use sampling logic here
        self.records.append(json_log_record)

    def flush(self):
        if len(self.records) > 0:
            # TODO: do cloud push for aws, s3 when we do k8s
            file_path = join(self.store_config['local']['directory'],
                             self.run_id, "samples", self.connector, f'{self.metric_type}.vals')
            dir_name = os.path.dirname(file_path)
            os.makedirs(dir_name, exist_ok=True)
            with open(file_path, "a+") as f:
                for record in self.records:
                    f.write(record.record.rejection_code if record.record.rejected else "200")
                    f.write(MAGIC_DELIM)
                    f.write(record.record.synthetic_record_id if record.record.synthetic_record_id else str(uuid4()))
                    f.write(MAGIC_DELIM)
                    f.write(json.dumps(record.record.data if record.record.data else {}))
                    f.write(MAGIC_DELIM)
                    f.write(record.record.rejection_message if record.record.rejection_message else "")
                    f.write(MAGIC_DELIM)
                    f.write(json.dumps(record.record.rejection_metadata if record.record.rejection_metadata else {}))
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
    def reset(self):
        pass


class ChunkEndFlushPolicy(FlushPolicy):
    def __init__(self, *args, **kwargs):
        super(ChunkEndFlushPolicy, self).__init__(*args, **kwargs)
        self.reset()

    def flush_required(self):
        if self.data_chunk_flushed:
            return True
        return False

    def set_data_chunk_flushed(self):
        self.data_chunk_flushed = True

    def reset(self):
        self.data_chunk_flushed = False


def main():
    from ..valmi_protocol import ValmiFinalisedRecordMessage
    store_config_str = "{\"provider\": \"local\", \"local\": {\"directory\": \"/tmp/shared_dir/test_logs\", \"max_lines_per_file_hint\" : 100, \"log_flush_interval\": 5}}"

    for i in range(100000):
        sample_writer = SampleWriter.get_writer_by_metric_type(store_config_str, "sync_id", "run_id", "connector", "succeeded")
        sample_writer.write(AirbyteMessage(type=Type.RECORD,
                                           record=ValmiFinalisedRecordMessage(synthetic_record_id="",
                                            data={"a": "b"},
                                            rejected=False if i%2 == 0 else True,
                                            metric_type="success" if i%2 == 0 else "failed",
                                            rejection_code="200" if i%2 == 0 else "100",
                                            stream="stream",
                                            emitted_at=int(time.time()*1000),
                                            rejection_message="i dont know",
                                            rejection_metadata={"c": "d"},
                                            )))
        time.sleep(0.1)
        sample_writer.data_chunk_flush_callback()


if __name__ == "__main__":
    main()
