"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, March 8th 2023, 11:38:42 am
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
from typing import Any, Dict, Iterable, Mapping
import socket
from contextlib import closing
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status
from .custom_http_sink import CustomHttpSink
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ConfiguredValmiDestinationCatalog,
    ConfiguredValmiCatalog,
    ValmiSink,
    DestinationSyncMode,
    FieldCatalog,
)
from valmi_connector_lib.destination_wrapper.destination_write_wrapper import (
    DestinationWriteWrapper,
    HandlerResponseData,
)
from valmi_connector_lib.valmi_destination import ValmiDestination
from urllib.parse import urlparse


class WebhookWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.http_handler = CustomHttpSink(run_time_args=self.run_time_args)

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:
        self.http_handler.handle(
            self.config,
            self.configured_destination_catalog,
            msg.record.data,
            counter,
            run_time_args=self.run_time_args,
        )
        return HandlerResponseData(flushed=True)

    def finalise_message_handling(self):
        pass


class DestinationWebhook(ValmiDestination):
    def __init__(self):
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "write"}

    def write(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiCatalog,
        configured_destination_catalog: ConfiguredValmiDestinationCatalog,
        input_messages: Iterable[AirbyteMessage],
        state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:
        logger.info(state)
        webhook_writer = WebhookWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return webhook_writer.start_message_handling(input_messages)

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = []
        basic_field_catalog = FieldCatalog(
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            },
            allow_freeform_fields=True,
            supported_destination_ids=[],
        )
        sinks.append(
            ValmiSink(
                name="Webhook",
                label="Webhook",
                supported_destination_sync_modes=[
                    DestinationSyncMode.upsert,
                    DestinationSyncMode.mirror,
                    DestinationSyncMode.append,
                    DestinationSyncMode.update,
                    DestinationSyncMode.create,
                ],
                field_catalog={
                    DestinationSyncMode.upsert.value: basic_field_catalog,
                    DestinationSyncMode.mirror.value: basic_field_catalog,
                    DestinationSyncMode.append.value: basic_field_catalog,
                    DestinationSyncMode.update.value: basic_field_catalog,
                    DestinationSyncMode.create.value: basic_field_catalog,
                },
            )
        )
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            if not (config["url"].startswith("http://") or config["url"].startswith("https://")):
                raise Exception("invalid url")
            if "headers" in config:
                for header in config["headers"]:
                    kvpair = header.split(":")
                    if len(kvpair) < 2 or len(kvpair[0].strip()) == 0 or len(kvpair[1].strip()) == 0:
                        raise Exception("invalid header - should be of form <key>: <val>")

            # TODO: What checks make sense for a webhook? Currently just checking for port open
            url = config["url"]
            parsed = urlparse(url)
            scheme = parsed.scheme if parsed.scheme else "http"
            port = parsed.port if parsed.port else 80 if scheme == "http" else 443
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex((parsed.hostname, port)) == 0:
                    return AirbyteConnectionStatus(status=Status.SUCCEEDED)
                else:
                    return AirbyteConnectionStatus(status=Status.FAILED, message=f"Port {port} is not open")
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
