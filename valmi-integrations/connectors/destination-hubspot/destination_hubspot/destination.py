"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Monday, April 24th 2023, 7:51:41 am
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

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Status
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
)
from valmi_connector_lib.valmi_destination import ValmiDestination
from .hubspot_utils import HubspotClient
from valmi_connector_lib.destination_wrapper.destination_write_wrapper import DestinationWriteWrapper, HandlerResponseData


class HubspotWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.hub_client = HubspotClient(run_time_args=self.run_time_args)
        self.last_seen_sync_op = None   

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:

        sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]
        self.last_seen_sync_op = sync_op
        flushed, metrics, rejected_records = self.hub_client.add_to_queue(
            sync_op, counter, msg, self.config,
            configured_stream=self.configured_catalog.streams[0],
            sink=self.configured_destination_catalog.sinks[0])

        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)

    def finalise_message_handling(self):
        flushed, metrics, rejected_records = self.hub_client.flush(self.last_seen_sync_op, config=self.config, sink=self.configured_destination_catalog.sinks[0])
        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)


class DestinationHubspot(ValmiDestination):
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
        # Start handling messages

        hubspot_writer = HubspotWriter(logger, config, configured_catalog, configured_destination_catalog, state)
        return hubspot_writer.start_message_handling(input_messages)

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        hub_client = HubspotClient(run_time_args=None)
        return hub_client.get_sinks(config)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            hub_client = HubspotClient(run_time_args=None)
            hub_client.get_access_token_with_retry(config=config)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
