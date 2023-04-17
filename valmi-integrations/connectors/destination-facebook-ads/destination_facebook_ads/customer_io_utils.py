from typing import Any, Dict
from airbyte_cdk import AirbyteLogger
import requests
from io import StringIO
from valmi_lib.valmi_protocol import ValmiStream, ConfiguredValmiSink
import json
from .http_sink import HttpSink
from .run_time_args import RunTimeArgs


def get_region(site_id: str, tracking_api_key: str):
    headers = {"Authorization": f"Basic {site_id}:{tracking_api_key}"}

    conn = requests.get("https://track.customer.io/api/v1/accounts/region", headers=headers)
    if conn.text is None:
        raise Exception("Could not get region with provided credentials")
    return conn.text


class CustomerIOExt(CustomerIO):
    max_buffer_len = 500 * 1000 - 100  # from customer io docs
    logger = AirbyteLogger()

    def __init__(self, run_time_args: RunTimeArgs, *args, **kwargs):
        super(CustomerIOExt, self).__init__(*args, **kwargs)
        self.buffer = StringIO()
        self.written_len = self.buffer.write('{"batch":[')
        self.http_sink = HttpSink(run_time_args=run_time_args)
        self.first_in_batch = True

    def make_person_object(self, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        obj = {}
        obj["type"] = "person"
        obj["action"] = "identify"
        obj["identifiers"] = {"id": str(data[configured_stream.id_key])}  # TODO: take the id type from UI
        mapped_data = self.map_data(sink.mapping, self._sanitize(data))
        obj["attributes"] = mapped_data
        return obj

    def map_data(self, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for k, v in mapping.items():
            if k in data:
                mapped_data[v] = data[k]
        return mapped_data

    def add_to_queue(self, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink) -> bool:
        obj = self.make_person_object(data, configured_stream=configured_stream, sink=sink)
        s = json.dumps(obj)
        if self.written_len + len(s) + 1 > self.max_buffer_len:
            self.flush()
            return True
        else:
            if not self.first_in_batch:
                self.buffer.write(",")

            self.first_in_batch = False
            self.buffer.write(s)

            self.written_len = self.written_len + len(s) + 1
            return False

    def flush(self):
        if not self.first_in_batch:  # TODO: check if any records are added. Use a nice name
            self.buffer.write("]}")
            self.logger.debug(self.buffer.getvalue())
            self.http_sink.send(
                method="POST",
                url=self.get_batch_query_string(),
                data=self.buffer.getvalue(),
                headers={"Content-Type": "application/json"},
                auth=(self.site_id, self.api_key),
            )
            self.written_len = self.buffer.write('{"batch":[')
            self.first_in_batch = True

    def get_batch_query_string(self):
        return f"{self.base_url}/batch"
