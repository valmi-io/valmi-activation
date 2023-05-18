from datetime import datetime, timedelta
import json
from typing import Any, Dict, Mapping

from airbyte_cdk import AirbyteLogger
import requests

from .run_time_args import RunTimeArgs
from .http_sink import HttpSink
from .retry_decorators import retry_on_exception
from hubspot.auth.oauth import TokensApi

from valmi_connector_lib.valmi_protocol import (
    DestinationSyncMode,
    ValmiSink,
    DestinationIdWithSupportedSyncModes,
    ValmiDestinationCatalog,
    ValmiStream,
    ConfiguredValmiSink,
)

logger = AirbyteLogger()

API_URL = "https://api.hubapi.com"
REQ_TIMEOUT = 15


class HubspotClient:
    max_items_in_batch = 100

    access_token = None
    access_token_expires_in = None
    access_token_created_at = None

    object_map = {
        "Contact": {
            "props_url": "/crm/v3/properties/contacts",
            "batch_url": "/crm/v3/objects/contacts/batch/create",
            "supported_destination_ids_modes": [
                DestinationIdWithSupportedSyncModes(
                    destination_id="email", destination_sync_modes=[DestinationSyncMode.upsert]
                ),
                DestinationIdWithSupportedSyncModes(
                    destination_id="id", destination_sync_modes=[DestinationSyncMode.update]
                ),
            ],
        },
        "Company": {
            "props_url": "/crm/v3/properties/companies",
            "batch_url": "/crm/v3/objects/companies/batch/create",
            "supported_destination_ids_modes": [
                DestinationIdWithSupportedSyncModes(
                    destination_id="domain", destination_sync_modes=[DestinationSyncMode.upsert]
                ),
                DestinationIdWithSupportedSyncModes(
                    destination_id="id", destination_sync_modes=[DestinationSyncMode.update]
                ),
            ],
        },
    }

    def __init__(self, run_time_args: RunTimeArgs, *args, **kwargs):
        self.buffer = []
        self.http_sink = HttpSink(run_time_args=run_time_args)

    def map_data(self, mapping: Dict[str, str], data: Dict[str, Any]):
        mapped_data = {}
        for k, v in mapping.items():
            if k in data:
                mapped_data[v] = data[k]
        return mapped_data

    @retry_on_exception
    def get_access_token(self, config: Mapping[str, Any]):
        if (
            self.access_token_created_at is not None
            and self.access_token_expires_in is not None
            and self.access_token_created_at + timedelta(seconds=self.access_token_expires_in) > datetime.now()
        ):
            pass
        else:
            self.access_token_created_at = datetime.now()

            resp = TokensApi().create_token(
                grant_type="refresh_token",
                client_id=config["credentials"]["client_id"],
                client_secret=config["credentials"]["client_secret"],
                refresh_token=config["credentials"]["refresh_token"],
                _request_timeout=REQ_TIMEOUT,
            )

            self.access_token = resp.access_token
            self.access_token_expires_in = resp.expires_in

    def add_to_queue(
        self, data, config: Mapping[Dict, Any], configured_stream: ValmiStream, sink: ConfiguredValmiSink
    ) -> bool:
        obj = self.map_data(sink.mapping, data)
        self.buffer.append({"properties": obj})
        if len(self.buffer) >= self.max_items_in_batch:
            self.flush(config, sink)
            return True
        return False

    def flush(self, config: Mapping[Dict, Any], sink: ConfiguredValmiSink):
        self.get_access_token(config)
        logger.debug(json.dumps({"inputs": self.buffer}))
        self.http_sink.send(
            method="POST",
            url=f"{API_URL}{self.object_map[sink.sink.name]['batch_url']}",
            data=None,
            json={"inputs": self.buffer},
            headers={"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"},
            auth=None,
        )
        self.buffer.clear()

    def get_sinks(self, config: Mapping[str, Any]):
        # api_client = ApiClient()
        self.get_access_token(config)

        sinks = []
        for k, v in self.object_map.items():
            obj_name = k
            obj_id = k
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            }

            props_url = v["props_url"]
            resp = requests.get(
                f"{API_URL}{props_url}", timeout=REQ_TIMEOUT, headers={"Authorization": f"Bearer {self.access_token}"}
            ).json()

            for result in resp["results"]:
                if "modificationMetadata" in result and result["modificationMetadata"]["readOnlyValue"]:
                    continue

                json_schema["properties"][result["name"]] = {}
                json_schema["properties"][result["name"]]["type"] = result["type"]
                json_schema["properties"][result["name"]]["description"] = result["description"]
                json_schema["properties"][result["name"]]["label"] = result["label"]

            sinks.append(
                ValmiSink(
                    name=f"{obj_name}",
                    id=f"{obj_id}",
                    supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.update],
                    json_schema=json_schema,
                    allow_freeform_fields=False,
                    supported_destination_ids_modes=v["supported_destination_ids_modes"],
                )
            )
        return ValmiDestinationCatalog(sinks=sinks)
