from datetime import datetime
from typing import Any, Dict
from airbyte_cdk import AirbyteLogger
import requests
from customerio import CustomerIO
from io import StringIO
from valmi_connector_lib.valmi_protocol import ValmiStream, ConfiguredValmiSink, ValmiRejectedRecordMessage
import json
from .http_sink import HttpSink
from valmi_connector_lib.common.run_time_args import RunTimeArgs
from requests.auth import HTTPBasicAuth
from valmi_connector_lib.common.metrics import get_metric_type


def get_region(site_id: str, tracking_api_key: str):
    conn = requests.get(
        "https://track.customer.io/api/v1/accounts/region", auth=HTTPBasicAuth(site_id, tracking_api_key)
    )
    if conn.text is None or conn.json() is None or "region" not in conn.json():
        raise Exception("Could not get region with provided credentials")
    return conn.json()["region"]


class CustomerIOExt(CustomerIO):
    max_buffer_len = 500 * 1000 - 100  # from customer io docs
    logger = AirbyteLogger()

    def __init__(self, run_time_args: RunTimeArgs, *args, **kwargs):
        super(CustomerIOExt, self).__init__(*args, **kwargs)
        self.buffer = StringIO()
        self.written_len = self.buffer.write('{"batch":[')
        self.http_sink = HttpSink(run_time_args=run_time_args)
        self.first_in_batch = True
        self.messages = []
        self.run_time_args = run_time_args

    def make_person_object(self, counter, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        obj = {}
        obj["type"] = "person"
        obj["action"] = "identify"
        # obj["identifiers"] = {"id": str(data[configured_stream.id_key]) if counter % 2 == 0 else 2}  # TODO: take the id type from UI
        obj["identifiers"] = {"id": str(data[configured_stream.id_key])}  # TODO: take the id type from UI
        mapped_data = self.map_data(sink.mapping, self._sanitize(data))
        obj["attributes"] = mapped_data
        return obj

    def map_data(self, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for item in mapping:
            k = item["stream"]
            v = item["sink"]
            if k in data:
                mapped_data[v] = data[k]
        return mapped_data

    def add_to_queue(self, counter, msg, configured_stream: ValmiStream, sink: ConfiguredValmiSink) -> bool:
        is_flush_forced = False
        if (counter) % self.run_time_args.chunk_size == 0:
            # Chunk Boundary - Flush needs to be forced
            is_flush_forced = True

        obj = self.make_person_object(counter, msg.record.data, configured_stream=configured_stream, sink=sink)
        s = json.dumps(obj)

        can_accommodate_new_obj = True
        if self.written_len + len(s) + 1 > self.max_buffer_len:
            can_accommodate_new_obj = False

        sync_op = sink.destination_sync_mode.value

        flushed = False
        metrics = {get_metric_type(sync_op): 0}
        rejected_records = []

        if not can_accommodate_new_obj:
            metrics, rejected_records = self.flush(sync_op)
            flushed = True

        if is_flush_forced and can_accommodate_new_obj:
            if not self.first_in_batch:
                self.buffer.write(",")
            self.messages.append(msg.record)
            self.buffer.write(s)
            self.written_len = self.written_len + len(s) + 1
            metrics, rejected_records = self.flush(sync_op)
            flushed = True
            return flushed, metrics, rejected_records

        if not self.first_in_batch:
            self.buffer.write(",")

        self.first_in_batch = False
        self.messages.append(msg.record)
        self.buffer.write(s)

        if is_flush_forced:
            new_metrics, new_rejected_records = self.flush(sync_op)
            flushed = True
            metrics = {
                get_metric_type(sync_op): metrics[get_metric_type(sync_op)] + new_metrics[get_metric_type(sync_op)]
            }
            rejected_records = rejected_records.extend(new_rejected_records)
        return flushed, metrics, rejected_records

    def generate_rejected_message_from_record(self, record, error):
        return ValmiRejectedRecordMessage(
            stream=record.stream,
            data=record.data,
            rejected=True,
            rejection_message=f'reason: {error["reason"]} -  fields: {error["field"]} - message: {error["message"]}',
            rejection_code="207",
            rejection_metadata=error,
            emitted_at=int(datetime.now().timestamp()) * 1000,
        )

    def flush(self, sync_op):
        if not self.first_in_batch:  # TODO: check if any records are added. Use a nice name
            self.buffer.write("]}")
            payload = self.buffer.getvalue()
            # self.logger.debug(payload)
            response = self.http_sink.send(
                method="POST",
                url=self.get_batch_query_string(),
                data=payload,
                headers={"Content-Type": "application/json"},
                auth=(self.site_id, self.api_key),
            )
            if response.status_code in (207, 400):
                # Some records failed.
                metrics = {
                    get_metric_type(sync_op): len(self.messages) - len(response.json()["errors"]),
                    get_metric_type("reject"): len(response.json()["errors"]),
                }
                rejected_records = [
                    self.generate_rejected_message_from_record(self.messages[error["batch_index"]], error)
                    for error in response.json()["errors"]
                ]
            else:
                metrics = {get_metric_type(sync_op): len(self.messages)}
                rejected_records = []

            # self.logger.debug(response.text)
            self.buffer = StringIO()
            self.written_len = self.buffer.write('{"batch":[')
            self.first_in_batch = True
            self.messages.clear()
            return metrics, rejected_records
        return {}, []

    def get_batch_query_string(self):
        return f"{self.base_url}/batch"
