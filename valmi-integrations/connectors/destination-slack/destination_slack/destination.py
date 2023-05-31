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
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteStateMessage, AirbyteMessage, Status
from airbyte_cdk.models.airbyte_protocol import Type, AirbyteStateType
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    FieldCatalog,
    DestinationWriteWrapper,
)
from valmi_connector_lib.valmi_destination import ValmiDestination
from valmi_connector_lib.common.run_time_args import RunTimeArgs
from datetime import datetime
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
        # Invite  bot this to the selected channel
        client = WebClient(token=config["credentials"]["access_token"])

        response = client.conversations_join(channel=configured_destination_catalog.sinks[0].sink.name)
        if not response["ok"]:
            raise Exception(response["message"]["error"])

        # Start handling messages

        counter = 0
        chunk_id = 0
        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

        for message in input_messages:
            now = datetime.now()

            if message.type == Type.RECORD:
                record = message.record
                mapped_data = map_data(configured_destination_catalog.sinks[0].mapping, record.data)

                response = client.chat_postMessage(
                    channel=configured_destination_catalog.sinks[0].sink.name, text=str(mapped_data)
                )

                counter = counter + 1
                if counter % run_time_args.chunk_size == 0:
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            type=AirbyteStateType.STREAM,
                            data={
                                "records_delivered": {DestinationSyncMode.append.value: counter},
                                "chunk_id": chunk_id,
                                "finished": False,
                            },
                        ),
                    )
                    counter = 0
                    chunk_id = chunk_id + 1

                if (datetime.now() - now).seconds > 5:
                    logger.info("A log every 5 seconds - is this required??")

                # slack lets 1 message per second
                time.sleep(1)

        # Sync completed - final state message
        yield AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                data={
                    "records_delivered": {DestinationSyncMode.append.value: counter},
                    "chunk_id": chunk_id,
                    "finished": True,
                },
            ),
        )

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
                    label=f"{channel_name} - {channel_id}",
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
