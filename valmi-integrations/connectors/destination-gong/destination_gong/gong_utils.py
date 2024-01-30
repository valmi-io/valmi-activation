"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Monday, June 5th 2023, 2:55:14 pm
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


from collections import namedtuple
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union
from airbyte_cdk import AirbyteLogger
import requests
from valmi_connector_lib.valmi_protocol import ValmiStream, ConfiguredValmiSink, ValmiFinalisedRecordMessage
from valmi_connector_lib.common.run_time_args import RunTimeArgs
from airbyte_cdk.sources.streams.http.http import HttpStream
from requests import Request
import json
import random

SyncOpResponse = namedtuple("SyncOpResponse", ["obj", "rejected", "rejected_record"], defaults=[None, False, None])
BASE_API_URL = "https://us-68970.api.gong.io"


# TODO: Use batch api for Gong. Currently doing one by one
class GongUtils(HttpStream):
    airbyte_logger = AirbyteLogger()

    def __init__(
        self, config: Mapping[str, Any], sink: ConfiguredValmiSink, run_time_args: RunTimeArgs, *args, **kwargs
    ):
        super().__init__(None)
        self.run_time_args = run_time_args
        self.access_key = config["access_key"]
        self.access_key_secret = config["access_key_secret"]
        self.integration_id = sink.sink.integrationId

        self.clientRequestId = random.randint(0, 1000000000)

    def make_object(self, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        mapped_data = self.map_data(sink.mapping, data)
        mapped_data[sink.destination_id] = data[configured_stream.id_key]
        return mapped_data

    def map_data(self, mapping: list[Dict[str, str]], data: Dict[str, Any]):
        mapped_data = {}
        for item in mapping:
            k = item["stream"]
            v = item["sink"]
            if k in data:
                # Special handling for datetime
                if v == "modifiedDate":
                    mapped_data[v] = datetime.fromisoformat(data[k]).replace(microsecond=0).astimezone().isoformat()
                else:
                    mapped_data[v] = data[k]
        return mapped_data

    def upsert(self, record, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        resp = self.make_request(sink, self.make_object(record.data, configured_stream, sink))
        return SyncOpResponse(obj=resp.json())

    def update(self, record, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        mapped_object = self.make_object(record.data, configured_stream, sink)

        is_present = False
        object_id = mapped_object["objectId"]
        s = requests.session()
        req = Request(
            method="GET",
            url=f"{BASE_API_URL}/v2/crm/entities",
            params={
                "integrationId": self.integration_id,
                "objectType": sink.name,
            },
            json=[object_id],
            auth=(self.access_key, self.access_key_secret),
        )
        prepped = s.prepare_request(req)
        resp = self._send_request(prepped, request_kwargs={"timeout": self.run_time_args.http_timeout})

        objects_map = resp.json()["crmObjectsMap"]
        if object_id in objects_map and objects_map[object_id] is not None:
            is_present = True

        if is_present:
            resp = self.make_request(sink, self.make_customer_object(record.data, configured_stream, sink))
            return SyncOpResponse(obj=resp.json())
        else:
            return SyncOpResponse(
                rejected=False,
                rejected_record=self.generate_rejected_message_from_record(
                    record, "Object not found", "404", "ignore"
                ),
            )

    def make_request(self, sink, request_obj):
        self.clientRequestId = self.clientRequestId + 1
        s = requests.session()
        self.airbyte_logger.debug(f"Request Object: {request_obj}")
        params = {
            "integrationId": self.integration_id,
            "objectType": sink.sink.name,
            "clientRequestId": str(self.clientRequestId),
        }
        self.airbyte_logger.debug(f"Params: {params}")
        req = Request(
            method="POST",
            url=f"{BASE_API_URL}/v2/crm/entities",
            auth=(self.access_key, self.access_key_secret),
            files={"dataFile": json.dumps(request_obj)},
            params={
                "integrationId": self.integration_id,
                "objectType": sink.sink.name,
                "clientRequestId": str(self.clientRequestId),
            },
        )
        prepped = s.prepare_request(req)
        return self._send_request(prepped, request_kwargs={"timeout": self.run_time_args.http_timeout})

    def generate_rejected_message_from_record(self, record, error_reason, error_code, metric_type):
        return ValmiFinalisedRecordMessage(
            stream=record.stream,
            data=record.data,
            rejected=True,
            rejection_message=error_reason,
            rejection_code=error_code,
            rejection_metadata={},
            metric_type=metric_type,
            emitted_at=int(datetime.now().timestamp()) * 1000,
        )

    def should_retry(self, response: requests.Response) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        self.clientRequestId = self.clientRequestId + 1
        return response.status_code == 429 or 500 <= response.status_code < 600

    ##############################################################################################
    # Dummy methods to satisfy the abstract class

    def url_base(self) -> str:
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return None

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return

    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None
