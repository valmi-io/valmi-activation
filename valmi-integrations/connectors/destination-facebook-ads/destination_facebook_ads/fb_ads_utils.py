from collections import defaultdict
from datetime import datetime
from typing import Any, Mapping, Optional, Union
from airbyte_cdk import AirbyteLogger
from requests_cache import Request, Response
from valmi_connector_lib.valmi_protocol import (
    ValmiStream,
    ConfiguredValmiSink,
    ValmiFinalisedRecordMessage
)
from valmi_connector_lib.common.metrics import get_metric_type
from valmi_connector_lib.common.run_time_args import RunTimeArgs
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from airbyte_cdk.sources.streams.http.rate_limiting import user_defined_backoff_handler, default_backoff_handler
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException


class FBAdsUtils:
    logger = AirbyteLogger()

    def __init__(self, config: Mapping[str, Any], run_time_args: RunTimeArgs, *args, **kwargs):
        credentials = config["credentials"]
        FacebookAdsApi.init(credentials["app_id"], credentials["app_secret"],
                            credentials["long_term_acccess_token"], crash_log=False)

        self.msgs = []
        self.users = []
        self.schema = None
        self.lookup_keys = None
        self.is_deleting = True
        self.run_time_args = run_time_args

    def get_custom_audience_schema(self):
        key_types = [
            CustomAudience.Schema.MultiKeySchema.extern_id,
            CustomAudience.Schema.MultiKeySchema.email,
            CustomAudience.Schema.MultiKeySchema.phone,
            CustomAudience.Schema.MultiKeySchema.gen,
            CustomAudience.Schema.MultiKeySchema.doby,
            CustomAudience.Schema.MultiKeySchema.dobm,
            CustomAudience.Schema.MultiKeySchema.dobd,
            CustomAudience.Schema.MultiKeySchema.ln,
            CustomAudience.Schema.MultiKeySchema.fn,
            CustomAudience.Schema.MultiKeySchema.fi,
            CustomAudience.Schema.MultiKeySchema.ct,
            CustomAudience.Schema.MultiKeySchema.st,
            CustomAudience.Schema.MultiKeySchema.zip,
            CustomAudience.Schema.MultiKeySchema.madid,
            CustomAudience.Schema.MultiKeySchema.country,
            CustomAudience.Schema.MultiKeySchema.appuid,
        ]

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {key_type: {"type": "string"} for key_type in key_types},
        }

    # TODO: define validations such as email validations and phone validations, run them here, and return valid and invalid records as a tuple
    def run_validations(self, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        return [[msg.record for msg in self.msgs], []]
    
    def add_to_queue(self, counter, msg, configured_stream: ValmiStream, sink: ConfiguredValmiSink) -> bool:
        data = msg.record.data
        sync_op = data["_valmi_meta"]["_valmi_sync_op"]

        metrics = defaultdict(lambda: 0)
        rejected_records = []
        flushed = False
        if sync_op == "delete":
            self.msgs.append(msg)
            # Both of the below conditions are actually same
            if len(self.msgs) >= self.run_time_args.chunk_size or counter % self.run_time_args.chunk_size == 0:
                flushed, metrics, rejected_records = self.flush(configured_stream, sink)
            return flushed, metrics, rejected_records
        else:
            # Delete mode done, now Upsert mode
            if self.is_deleting:
                flushed, metrics, rejected_records = self.flush(configured_stream, sink)

            # initialise schema and lookup_keys only once
            if self.schema is None:
                self.schema = [sink.destination_id]
                self.lookup_keys = [configured_stream.id_key]

                for k, v in sink.mapping.items():
                    self.schema.extend(v)
                    self.lookup_keys.extend(k)

            self.msgs.append(msg)
            # Both of the below conditions are actually same
            if len(self.msgs) >= self.run_time_args.chunk_size or counter % self.run_time_args.chunk_size == 0:
                flushed, new_metrics, new_rejected_records = self.flush(configured_stream, sink)
                metrics = self.merge_metric_dictionaries(metrics, new_metrics)
                rejected_records.extend(new_rejected_records)
            return flushed, metrics, rejected_records

    def generate_rejected_message_from_record(self, record, error_code, error_msg, metric_type):
        return ValmiFinalisedRecordMessage(
            stream=record.stream,
            data=record.data,
            rejected=True,
            rejection_message=error_msg,
            rejection_code=error_code,
            rejection_metadata={},
            metric_type=metric_type,
            emitted_at=int(datetime.now().timestamp()) * 1000,
        )

    def merge_metric_dictionaries(self, m1, m2):
        for k, v in m1.items():
            if k in m2:
                m2[k] += v
            else:
                m2[k] = v
        return m2
    
    def flush(self, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        valid_records, rejected_records = self.run_validations(configured_stream, sink)
        metrics = defaultdict(lambda: 0)
        metrics[get_metric_type("fail")] = len(rejected_records)

        if self.is_deleting:
            if len(valid_records) > 0:
                user_list = [[record.data[configured_stream.id_key]] for record in valid_records]
                self.make_request(
                    CustomAudience(sink.sink.name).remove_users,
                    [sink.destination_id],
                    [user_list],
                    True,
                )
            metrics[get_metric_type("delete")] = len(valid_records)
            self.is_deleting = False
            self.msgs.clear()
        else:
            user_list = [[record.data[key] for key in self.lookup_keys] for record in valid_records]
            self.make_request(
                CustomAudience(sink.sink.name).add_users,
                self.schema,
                user_list,
                True)
            metrics[get_metric_type("upsert")] = len(valid_records)
            self.msgs.clear()
        return True, metrics, rejected_records
    
    def _fn_exception_handler(self, fn, schema, users, is_raw):
        try:
            return fn(schema, users, is_raw)
        except FacebookRequestError as e:
            if (self.should_retry(e)):
                dummy_http_request = Request()
                dummy_http_response = Response()
                error_message = str(e)
                custom_backoff_time = self.backoff_time()
                if custom_backoff_time:
                    raise UserDefinedBackoffException(
                        backoff=custom_backoff_time,
                        request=dummy_http_request,
                        response=dummy_http_response,
                        error_message=error_message,
                    )
                else:
                    raise DefaultBackoffException(
                        request=dummy_http_request, response=dummy_http_response, error_message=error_message
                    )

            raise e

    def make_request(self, fn, schema, users, is_raw):
        self.max_tries = self.max_retries
        if self.max_tries is not None:
            max_tries = max(0, self.max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries)(self._fn_exception_handler)
        backoff_handler = default_backoff_handler(max_tries=max_tries, factor=self.retry_factor)
        return backoff_handler(user_backoff_handler)(fn, schema, users, is_raw)

    ### Retry behavior Logic used by the backoff closures ###
    @property
    def max_retries(self) -> Union[int, None]:
        return self.run_time_args.max_retries

    @property
    def retry_factor(self) -> float:
        return 5

    def backoff_time(self) -> Optional[float]:
        """
        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def should_retry(self, facebookRequestError: FacebookRequestError) -> bool:
        if facebookRequestError.api_transient_error() or facebookRequestError.api_error_code() in (4, 17, 341):
            # Throttled or temporarily unavailable  
            return True
        return False
