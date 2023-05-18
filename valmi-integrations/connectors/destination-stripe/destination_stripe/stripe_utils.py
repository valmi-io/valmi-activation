"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Monday, May 1st 2023, 12:30:00 pm
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

import json
from typing import Any, Dict, Mapping, Union
from airbyte_cdk import AirbyteLogger
from valmi_connector_lib.valmi_protocol import ValmiStream, ConfiguredValmiSink
from .run_time_args import RunTimeArgs
from airbyte_cdk.sources.streams.http.rate_limiting import user_defined_backoff_handler, default_backoff_handler
from jsonpath_ng import parse
import stripe


class StripeUtils:
    logger = AirbyteLogger()

    def __init__(self, config: Mapping[str, Any], run_time_args: RunTimeArgs, *args, **kwargs):
        self.run_time_args = run_time_args
        # Inititalise API key
        self.api_key = config["api_key"]

    def make_customer_object(self, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        # obj["id"] = {"id": str(data[configured_stream.id_key])} # We are using only email for the id  # TODO: take the id type from UI
        mapped_data = self.map_data(sink.mapping, data)
        mapped_data["email"] = data[configured_stream.id_key]

        return mapped_data

    def map_data(self, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for k, v in mapping.items():
            if k in data:
                # Create json object from json_path
                parse(v).update_or_create(mapped_data, data[k])
                # mapped_data[v] = data[k]
        return mapped_data

    def _customer_query(self, request_obj):
        stripe.Customer.create(api_key=self.api_key, **request_obj)
        pass

    @property
    def max_retries(self) -> Union[int, None]:
        return self.run_time_args.max_retries

    @property
    def retry_factor(self) -> float:
        return 5

    def make_request(self, request_obj):
        self.max_tries = self.max_retries
        if self.max_tries is not None:
            max_tries = max(0, self.max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries)(self._customer_query)
        backoff_handler = default_backoff_handler(max_tries=max_tries, factor=self.retry_factor)
        return backoff_handler(user_backoff_handler)(request_obj)

    def upsert(self, record, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        self.logger.debug(json.dumps(self.make_customer_object(record.data, configured_stream, sink)))
        self.make_request(self.make_customer_object(record.data, configured_stream, sink))

    def update(self, record, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        self.logger.debug(json.dumps(self.make_customer_object(record.data, configured_stream, sink)))
        self.make_request(self.make_customer_object(record.data, configured_stream, sink))

        # self.make_request(record)
