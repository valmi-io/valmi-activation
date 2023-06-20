from collections import defaultdict
from datetime import datetime
from typing import Any, Mapping, Optional, Union, List, Dict
from airbyte_cdk import AirbyteLogger
from requests_cache import Request, Response
from valmi_connector_lib.valmi_protocol import (
    ValmiStream,
    ConfiguredValmiSink,
    ValmiFinalisedRecordMessage
)

from valmi_connector_lib.common.metrics import get_metric_type
from valmi_connector_lib.common.run_time_args import RunTimeArgs
from airbyte_cdk.sources.streams.http.rate_limiting import user_defined_backoff_handler, default_backoff_handler
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException

import jinja2
import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError, RESOURCE_EXHAUSTED, UNAVAILABLE
from airbyte_cdk.models import AirbyteMessage
import time
import json

MAX_CHUNK_SIZE = 500


def map_data(mapping: list[Dict[str, str]], data: Dict[str, Any]):
    mapped_data = {}
    if "_valmi_meta" in data:
        mapped_data["_valmi_meta"] = data["_valmi_meta"]
    for item in mapping:
        k = item["stream"]
        v = item["sink"]
        if k in data:
            mapped_data[v] = data[k]
    return mapped_data


def get_jinja_template(template_str: str):
    if template_str is None:
        return None

    environment = jinja2.Environment()
    template = environment.from_string(template_str)
    return template


class FCMUtils:
    logger = AirbyteLogger()

    def __init__(self, config: Mapping[str, Any], run_time_args: RunTimeArgs, *args, **kwargs):
        service_ac_credentials_str = config["service_account"]
        service_ac_credentials = json.loads(service_ac_credentials_str)
        creds = credentials.Certificate(service_ac_credentials)
        self.app = firebase_admin.initialize_app(creds)

        self.title_template = get_jinja_template(kwargs.get("title_template", None))
        self.body_template = get_jinja_template(kwargs.get("body_template", None))
        self.field_mapping = kwargs.get("field_mapping", None)

        # Max cap on chunk size
        self.chunk_size = MAX_CHUNK_SIZE
        if run_time_args and run_time_args.chunk_size:
            if run_time_args.chunk_size < MAX_CHUNK_SIZE:
                self.chunk_size = run_time_args.chunk_size

        self.run_time_args = run_time_args
        self.msgs: List[AirbyteMessage] = []
        self.fcm_msgs: List[messaging.Notification] = []

    def get_cloud_messaging_schema(self):
        """
            To send a message to a combination of topics, specify a condition, 
            which is a boolean expression that specifies the target topics. For example, 
            the following condition will send messages to devices that are subscribed to TopicA and either TopicB or TopicC:

            "'TopicA' in topics && ('TopicB' in topics || 'TopicC' in topics)"

            FCM first evaluates any conditions in parentheses, and then evaluates the expression from left to right. 
            In the above expression, a user subscribed to any single topic does not receive the message. 
            Likewise, a user who does not subscribe to TopicA does not receive the message. These combinations do receive it:
                TopicA and TopicB
                TopicA and TopicC

            You can include up to five topics in your conditional expression.
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "device_id": {"type": "string"},
                "image_url": {"type": "string"},
                "topic": {"type": "string"},
                "condition_on_topics": {"type": "string"},
            }
        }

    def create_fcm_message(self, data: Dict) -> messaging.Notification:
        data_mappping = {}
        if self.field_mapping:
            data_mappping = map_data(self.field_mapping, data)

        title = self.title_template.render(data_mappping)
        body = self.body_template.render(data_mappping)
        image = data_mappping.pop("image_url", None)
        token = data_mappping.pop("device_id", None)
        topic = data_mappping.pop("topic", None)
        condition = data_mappping.pop("condition_on_topics", None)

        notification = messaging.Notification(title=title, body=body, image=image)
        message = messaging.Message(notification=notification, token=token, topic=topic, condition=condition)
        return message

    def add_to_queue(self, counter, msg, configured_stream: ValmiStream, sink: ConfiguredValmiSink) -> bool:
        data = msg.record.data
        sync_op = data["_valmi_meta"]["_valmi_sync_op"]

        metrics = defaultdict(lambda: 0)
        rejected_records = []
        flushed = False

        # There is no concept of delete in FCM
        if sync_op == "delete":
            return flushed, metrics, rejected_records

        fcm_msg = self.create_fcm_message(data)
        self.fcm_msgs.append(fcm_msg)
        self.msgs.append(msg)

        if len(self.msgs) >= self.chunk_size:
            # Sleep for 1 proper error logging
            time.sleep(1)
            flushed, new_metrics, new_rejected_records = self.flush(configured_stream, sink)
            metrics = self.merge_metric_dictionaries(metrics, new_metrics)
            rejected_records.extend(new_rejected_records)

        return flushed, metrics, rejected_records

    def generate_rejected_message_from_record(self, record, error_code, error_msg, metric_type, metadata={}):
        return ValmiFinalisedRecordMessage(
            stream=record.stream,
            data=record.data,
            rejected=True,
            rejection_message=error_msg,
            rejection_code=error_code,
            rejection_metadata=metadata,
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
        metrics = defaultdict(lambda: 0)

        """
        Automatic retries (https://firebase.google.com/docs/reference/admin/error-handling)

            The Admin SDK automatically retries certain errors before exposing those errors to the users. In general, 
            following types of errors are transparently retried:

                All API errors resulting from HTTP 503 (Service Unavailable) responses.
                Some API errors resulting from HTTP 500 (Internal Server Error) responses.
                Most low-level I/O errors (connection refused, connection reset etc).

            The SDK will retry each of the above errors up to 5 times (the original attempt + 4 retries) with exponential backoff. 
            You can implement your own retry mechanisms at the application level if you want, but this is typically not required.
        """
        batch_response = self.make_request(messaging.send_all, self.fcm_msgs)

        rejected_records = []
        for i, response in enumerate(batch_response.responses):
            msg = self.msgs[i]
            op_type = msg.record.data["_valmi_meta"]["_valmi_sync_op"]
            if response.success:
                metrics[get_metric_type(op_type)] += 1
            else:
                metrics[get_metric_type("fail")] += 1
                meta_data = {
                    "cause": str(response.exception.cause)
                }
                rejected_msg = self.generate_rejected_message_from_record(
                    msg.record,
                    response.exception.code,
                    str(response.exception),
                    get_metric_type(op_type),
                    meta_data
                )
                rejected_records.append(rejected_msg)

        self.fcm_msgs = []
        self.msgs = []

        return True, metrics, rejected_records
    
    def _fcm_exception_handler(self, func, messages):
        try:
            return func(messages)
        except FirebaseError as e:
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
        except ValueError as e:
            raise e

    def make_request(self, func, messages):
        self.max_tries = self.max_retries
        if self.max_tries is not None:
            max_tries = max(0, self.max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries)(self._fcm_exception_handler)
        backoff_handler = default_backoff_handler(max_tries=max_tries, factor=self.retry_factor)
        return backoff_handler(user_backoff_handler)(func, messages)

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

    def should_retry(self, firebaseError: FirebaseError) -> bool:

        """
        Retrying Errors
        
            Clients may retry on 503 UNAVAILABLE errors with exponential backoff. 
            The minimum delay should be 1s unless it is documented otherwise. 
            The default retry repetition should be once unless it is documented otherwise.

            For 429 RESOURCE_EXHAUSTED errors, the client may retry at the higher level with minimum 30s delay. 
            Such retries are only useful for long running background jobs.

            For all other errors, retry may not be applicable. First ensure your request is idempotent, 
            and see google.rpc.RetryInfo for guidance.
        """

        error_code = firebaseError.code()

        if error_code == RESOURCE_EXHAUSTED or error_code == UNAVAILABLE:
            return True

        return False
