from abc import abstractmethod
from collections import defaultdict
import json
from os.path import join
import os
from typing import List
from airbyte_cdk.models import (
    AirbyteMessage
)
from uuid import uuid4
from .constants import MAGIC_DELIM


class SampleWriter:
    writers = {}
    sync_id = None
    store_config_str = None
    run_id = None
    connector = None
    metric_type = None

    @classmethod
    def get_writer_by_metric_type(cls, store_config_str=None,
                                  sync_id=None, run_id=None, connector=None, metric_type=None):
        if sync_id is not None:
            SampleWriter.sync_id = sync_id
        if store_config_str is not None:
            SampleWriter.store_config_str = store_config_str
        if run_id is not None:
            SampleWriter.run_id = run_id
        if connector is not None:
            SampleWriter.connector = connector

        if metric_type is not None and \
            (metric_type not in SampleWriter.writers
             or SampleWriter.writers[metric_type] is None):
            SampleWriter.writers[metric_type] = SampleWriter(SampleWriter.store_config_str,
                                                             ChunkEndFlushPolicy(store_config_str=SampleWriter.store_config_str),
                                                             SampleWriter.sync_id,
                                                             SampleWriter.run_id,
                                                             SampleWriter.connector,
                                                             metric_type)
        if metric_type is not None:
            return SampleWriter.writers[metric_type]
        return None

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
        self.num_samples_per_code = int(os.environ.get("NUM_SAMPLES_PER_CODE", 10))
        self.sample_counter: dict[str, int] = defaultdict(lambda: 0)

    def reset(self):
        self.records.clear()
        self.flush_policy.reset()

    def check_for_flush(self):
        if self.flush_policy.flush_required():
            self.flush()
            self.reset()

    def write(self, json_log_record):
        rejection_code = json_log_record["record"]["rejection_code"] \
            if "rejected" in json_log_record["record"] and json_log_record["record"]["rejected"] else "200"
        if (self.sample_counter[rejection_code] < self.num_samples_per_code):
            self.sample_counter[rejection_code] += 1
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
                    f.write(record["record"]["rejection_code"] if "rejected" in record["record"] and record["record"]["rejected"] else "200")
                    f.write(MAGIC_DELIM)
                    f.write(record["record"]["synthetic_internal_id"] if "synthetic_internal_id" in record["record"] and record["record"]["synthetic_internal_id"] else str(uuid4()))
                    f.write(MAGIC_DELIM)
                    f.write(json.dumps(record["record"]["data"] if "data" in record["record"] and record["record"]["data"] else {}))
                    f.write(MAGIC_DELIM)
                    f.write(record["record"]["rejection_message"] if "rejection_message" in record["record"] and record["record"]["rejection_message"] else "")
                    f.write(MAGIC_DELIM)
                    f.write(json.dumps(record["record"]["rejection_metadata"] if "rejection_metadata" in record["record"] and record["record"]["rejection_metadata"] else {}))
                    f.write("\n")

    @classmethod
    def data_chunk_flush_callback(cls):
        for k, writer in SampleWriter.writers.items():
            writer.flush_policy.set_data_chunk_flushed()
            writer.check_for_flush()


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
    import time
    store_config_str = "{\"provider\": \"local\", \"local\": {\"directory\": \"/tmp/shared_dir/test_logs\", \"max_lines_per_file_hint\" : 100, \"log_flush_interval\": 5}}"

    for i in range(100000):
        sample_writer = SampleWriter.get_writer_by_metric_type(store_config_str, "sync_id", "run_id", "connector", "succeeded")
        sample_writer.write(AirbyteMessage(type=Type.RECORD,
                                           record=ValmiFinalisedRecordMessage(synthetic_internal_id="",
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
