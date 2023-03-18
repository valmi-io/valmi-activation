from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import requests
from valmi_protocol import ConfiguredValmiDestinationCatalog
from .run_time_args import RunTimeArgs

from airbyte_cdk.sources.streams.http.http import HttpStream
from requests import Request, Session


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
            req = Request("GET", config["url"], params=mapped_data, headers=headers)
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
            req = Request("POST", config["url"], data=payload, headers=headers)
            prepped = s.prepare_request(req)
            self._send_request(prepped, request_kwargs={"timeout": run_time_args.http_timeout})
        else:
            raise UnsupportedMethodException("Method not supported - not one of GET or POST")

    def map_data(self, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for k, v in mapping.items():
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
