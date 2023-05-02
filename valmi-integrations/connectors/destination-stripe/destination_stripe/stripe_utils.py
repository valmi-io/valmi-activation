import json
from typing import Any, Dict, Union
from airbyte_cdk import AirbyteLogger
from valmi_lib.valmi_protocol import ValmiStream, ConfiguredValmiSink
from .http_sink import HttpSink
from .run_time_args import RunTimeArgs
from airbyte_cdk.sources.streams.http.rate_limiting import user_defined_backoff_handler, default_backoff_handler
from jsonpath_ng import parse
import stripe


class StripeUtils:
    logger = AirbyteLogger()

    def __init__(self, run_time_args: RunTimeArgs, *args, **kwargs):
        self.http_sink = HttpSink(run_time_args=run_time_args)

    def make_customer_object(self, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        # obj["id"] = {"id": str(data[configured_stream.id_key])} # We are using only email for the id  # TODO: take the id type from UI
        mapped_data = self.map_data(sink.mapping, data)
        mapped_data["email"] = {"email": data[configured_stream.id_key]}

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
        stripe.Customer.create(request_obj)
        pass

    @property
    def max_retries(self) -> Union[int, None]:
        return self.run_time_args.max_retries

    def make_request(self, request_obj):
        max_tries = self.max_retries
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
