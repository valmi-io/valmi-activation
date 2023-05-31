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
import time
from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, Status
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    FieldCatalog,
    DestinationWriteWrapper,
    HandlerResponseData,
    get_metric_type,
)
from valmi_connector_lib.valmi_destination import ValmiDestination
from slack_sdk import WebClient
from .slack_utils import map_data


class SlackWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.client = WebClient(token=self.config["credentials"]["access_token"])

        response = self.client.conversations_join(channel=self.configured_destination_catalog.sinks[0].sink.name)
        if not response["ok"]:
            raise Exception(response["message"]["error"])

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:

        metrics = {}
        sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]

        rejected_records = []
        mapped_data = map_data(self.configured_destination_catalog.sinks[0].mapping, msg.record.data)

        # TODO: Handle JINJA templated fields
        
        response = self.client.chat_postMessage(
            channel=self.configured_destination_catalog.sinks[0].sink.name, text=str(mapped_data)
        )

        if not response["ok"]:
            raise Exception(response["message"]["error"])

        metrics[get_metric_type(sync_op)] = 1

        # slack lets 1 message per second
        time.sleep(1)
        return HandlerResponseData(flushed=True, metrics=metrics, rejected_records=rejected_records)

    def finalise_message_handling(self):
        pass


class DestinationSlack(ValmiDestination):
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
        # state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:
        slack_writer = SlackWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return slack_writer.start_message_handling(input_messages)

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        client = WebClient(token=config["credentials"]["access_token"])
        response = client.api_call("conversations.list", params=[])
        sinks = []
        basic_field_catalog = FieldCatalog(
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            },
            allow_freeform_fields=True,
            supported_destination_ids=[],
            templated_fields={
                "message": {
                    "type": "string",
                    "label": "Formatted Message",
                    "description": "Message to be sent to the channel. You can use jinja template with the mapped fields to format the message. For example: `{{name}}` will be replaced with the value of the `name` field. So you can write 'Hello {{name}}, ...'",
                    "required": True
                }
            },
        )
        for channel in response["channels"]:
            channel_name = channel["name"]
            channel_id = channel["id"]
            sinks.append(
                ValmiSink(
                    name=f"{channel_id}",
                    label=f"#{channel_name}",
                    supported_destination_sync_modes=[
                        DestinationSyncMode.append,
                    ],
                    field_catalog={ 
                        DestinationSyncMode.append.value: basic_field_catalog,
                    },
                )
            )
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            # Check if you can read the channel list
            client = WebClient(token=config["credentials"]["access_token"])
            response = client.api_call("conversations.list", params=[])
            if response["ok"]:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED,
                                               message=f'Unable to fetch Slack Channels. Error: {response["error"]}')
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
