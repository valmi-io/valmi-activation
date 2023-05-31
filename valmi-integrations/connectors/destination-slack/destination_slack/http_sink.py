from typing import Any, Iterable, List, Mapping, Optional, Union
from airbyte_cdk.sources.streams.http.http import HttpStream
from requests import Request, Session
import requests
from valmi_connector_lib.common.run_time_args import RunTimeArgs


class UnsupportedMethodException(Exception):
    pass


class HttpSink(HttpStream):
    def __init__(self, run_time_args: RunTimeArgs):
        super().__init__(None)
        self.run_time_args = run_time_args

    @property
    def max_retries(self) -> Union[int, None]:
        return self.run_time_args.max_retries

    def send(self, method, url, data, headers, auth):
        s = Session()
        req = Request(method, url, data=data, headers=headers, auth=auth)
        prepped = s.prepare_request(req)
        return self._send_request(prepped, request_kwargs={"timeout": self.run_time_args.http_timeout})

    def should_retry(self, response: requests.Response) -> bool:
        # Checking both status_code and text is a bit of a hack, but it's the only way to check for a 429
        retry = response.status_code == 429 or 500 <= response.status_code < 600
        if not retry:
            if response.text is not None:
                resp_json = response.json()
                if not resp_json["ok"]:
                    error = resp_json["error"]
                    if error in ["service_unavailable", "ratelimited"]:
                        retry = True
        return retry

    ##############################################################################################
    # TODO: DUMMY stuff to make it run
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
