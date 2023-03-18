from typing import Any, Dict, Mapping
from requests.adapters import HTTPAdapter, Retry
import requests
from valmi_protocol import ConfiguredValmiDestinationCatalog
from .run_time_args import RunTimeArgs


class UnsupportedMethodException(Exception):
    pass


class CustomHttpHandler:
    def __init__(self, run_time_args: RunTimeArgs) -> None:
        # extract sync_id from the run_time_args

        ## initalise requests session with retries
        req_session = requests.Session()
        # retry on all errors except 400 and 401
        status_forcelist = tuple(x for x in requests.status_codes._codes if x > 400 and x not in [400, 401])
        retries = Retry(total=run_time_args.max_retries, backoff_factor=0.1, status_forcelist=status_forcelist)
        req_session.mount("http://", HTTPAdapter(max_retries=retries))

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
            mapped_data["_sync_mode"] = catalog.sinks[0].destination_sync_mode
            r = requests.get(config["url"], params=mapped_data, headers=headers, timeout=run_time_args.http_timeout)
            return r
        elif config["method"] == "POST":
            payload = {
                "_message_id": record_counter,
                "_sync_mode": catalog.sinks[0].destination_sync_mode,
                "_type": "object",
                "payload": mapped_data,
            }
            r = requests.post(config["url"], headers=headers, timeout=run_time_args.http_timeout, data=payload)
            return r
        else:
            raise UnsupportedMethodException("Method not supported - not one of GET or POST")

    def map_data(self, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for k, v in mapping.items():
            if k in data:
                mapped_data[v] = data[k]
        return mapped_data
