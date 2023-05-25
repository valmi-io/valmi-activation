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

from typing import Any, Dict, Mapping, Optional, Union
from airbyte_cdk import AirbyteLogger
from requests import HTTPError
from requests_cache import Request, Response
import stripe
from valmi_connector_lib.valmi_protocol import ValmiStream, ConfiguredValmiSink
from valmi_connector_lib.common.run_time_args import RunTimeArgs
from airbyte_cdk.sources.streams.http.rate_limiting import user_defined_backoff_handler, default_backoff_handler
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException
from jsonpath_ng import parse
from stripe.error import StripeError


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
        for item in mapping:
            k = item["stream"]
            v = item["sink"]
            if k in data:
                # Create json object from json_path
                parse(v).update_or_create(mapped_data, data[k])
                # mapped_data[v] = data[k]
        return mapped_data

    def upsert(self, record, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        return self.make_request("upsert", self.make_customer_object(record.data, configured_stream, sink))

    def update(self, record, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        return self.make_request("update", self.make_customer_object(record.data, configured_stream, sink))

    def make_request(self, op, request_obj):
        self.max_tries = self.max_retries
        if self.max_tries is not None:
            max_tries = max(0, self.max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries)(self._customer_query)
        backoff_handler = default_backoff_handler(max_tries=max_tries, factor=self.retry_factor)
        return backoff_handler(user_backoff_handler)(op, request_obj)

    def _perform_upsert(self, request_obj):
        # check for existence
        customer_objs = stripe.Customer.list(api_key=self.api_key, email=request_obj["email"])
        if customer_objs and len(customer_objs.data) > 0:
            # just update the first object.
            return stripe.Customer.modify(api_key=self.api_key, sid=customer_objs.data[0]["id"], **request_obj)
        else:
            # not found, create the object.
            self.logger.debug("Customer not found")
            return stripe.Customer.create(api_key=self.api_key, **request_obj)

    def _perform_update(self, request_obj):
        # check for existence
        customer_objs = stripe.Customer.list(api_key=self.api_key, email=request_obj["email"])
        if customer_objs and len(customer_objs.data) > 0:
            # just update the first object.
            return stripe.Customer.modify(api_key=self.api_key, sid=customer_objs.data[0]["id"], **request_obj)
        return None

    def _customer_query(self, op, request_obj):
        dummy_http_request = Request()
        dummy_http_response = Response()
        error_message = ""
        exc = None
        try:
            if op == "upsert":
                return self._perform_upsert(request_obj)
            elif op == "update":
                return self._perform_update(request_obj)
        except stripe.error.InvalidRequestError as e:
            ## HANDLE Rejected sample request due to invalid request error.
            pass
        except stripe.error.RateLimitError as e:
            error_message = str(e)
            self.logger.error(error_message)
            dummy_http_response.status_code = 429
        except StripeError as e:
            error_message = str(e)
            self.logger.error(error_message)
            if e.http_status:
                dummy_http_response.status_code = e.http_status
            else:
                dummy_http_response.status_code = 500  # Assuming connect error
            exc = HTTPError(response=dummy_http_response)

        if self.should_retry(exc):
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
        elif self.raise_on_http_errors:
            # Raise any HTTP exceptions that happened in case there were unexpected ones
            self.raise_for_status(exc)
        pass

    ### Retry behavior Logic used by the backoff closures ###
    @property
    def raise_on_http_errors(self) -> bool:
        """
        Override if needed. If set to False, allows opting-out of raising HTTP code exception.
        """
        return True

    @property
    def max_retries(self) -> Union[int, None]:
        return self.run_time_args.max_retries

    @property
    def retry_factor(self) -> float:
        return 5

    def error_message(self, http_error: HTTPError) -> str:
        """
        Override this method to specify a custom error message which can incorporate the HTTP response received

        :param response: The incoming HTTP response from the partner API
        :return:
        """
        return ""

    def backoff_time(self) -> Optional[float]:
        """
        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def should_retry(self, http_error: HTTPError) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        return http_error.response.status_code == 429 or 500 <= http_error.response.status_code < 600

    def raise_for_status(self, http_error: HTTPError):
        """Raises :class:`HTTPError`, if one occurred."""
        """
        http_error_msg = ""
        if isinstance(self.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                reason = self.reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = self.reason.decode("iso-8859-1")
        else:
            reason = self.reason

        if 400 <= self.status_code < 500:
            http_error_msg = (
                f"{self.status_code} Client Error: {reason} for url: {self.url}"
            )

        elif 500 <= self.status_code < 600:
            http_error_msg = (
                f"{self.status_code} Server Error: {reason} for url: {self.url}"
            )

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)
        """
        raise http_error
