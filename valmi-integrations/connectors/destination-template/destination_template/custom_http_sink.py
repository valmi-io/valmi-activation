"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Saturday, March 18th 2023, 12:11:53 pm
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

from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import requests
from valmi_connector_lib.valmi_protocol import ConfiguredValmiDestinationCatalog
from valmi_connector_lib.common.run_time_args import RunTimeArgs

from airbyte_cdk.sources.streams.http.http import HttpStream
from requests import Request, Session

from flatten_json import flatten


class UnsupportedMethodException(Exception):
    pass


class CustomHttpSink(HttpStream):
    def __init__(self, run_time_args: RunTimeArgs):
        super().__init__(None)
        self.run_time_args = run_time_args

    @property
    def max_retries(self) -> Union[int, None]:
        return self.run_time_args.max_retries

    def handle(
        self,
        config: Mapping[str, Any],
        catalog: ConfiguredValmiDestinationCatalog,
        json_data,
        record_counter: int,
        run_time_args: RunTimeArgs,
    ):
        headers = (
            {header.split(":")[0].strip(): header.split(":")[1].strip() for header in config["headers"]}
            if "headers" in config
            else {}
        )
        mapped_data = self.map_data(catalog.sinks[0].mapping, json_data)

        if config["method"] == "GET":
            mapped_data["_message_id"] = record_counter
            mapped_data["_sync_mode"] = catalog.sinks[0].destination_sync_mode.value

            s = Session()
            req = Request("GET", config["url"], params=flatten(mapped_data), headers=headers)
            prepped = s.prepare_request(req)
            self._send_request(prepped, request_kwargs={"timeout": run_time_args.http_timeout})

        elif config["method"] == "POST":
            payload = {
                "_message_id": record_counter,
                "_sync_mode": catalog.sinks[0].destination_sync_mode.value,
                "_type": "object",
                "payload": mapped_data,
            }

            s = Session()
            req = Request("POST", config["url"], json=payload, headers=headers)
            prepped = s.prepare_request(req)
            self._send_request(prepped, request_kwargs={"timeout": run_time_args.http_timeout})
        else:
            raise UnsupportedMethodException("Method not supported - not one of GET or POST")

    def map_data(self, mapping: list[Dict[str, str]], data: Dict[str, Any]):
        mapped_data = {}
        if "_valmi_meta" in data:
            mapped_data["_valmi_meta"] = data["_valmi_meta"]
        for item in mapping:
            k = item["stream"]
            v = item["sink"]
            if k in data:
                mapped_data[v] = data[k]
        return mapped_data

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
