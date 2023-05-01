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
from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteStateMessage, AirbyteMessage, Status
from airbyte_cdk.models.airbyte_protocol import Type, AirbyteStateType
from valmi_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    DestinationIdWithSupportedSyncModes,
    ValmiSink,
)
from valmi_lib.valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs

from datetime import datetime
from .stripe_utils import StripeUtils
import stripe


class DestinationStripe(ValmiDestination):
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
        # Start handling messages

        counter = 0
        counter_by_type = {}
        chunk_id = 0
        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

        counter_by_type["upsert"] = 0
        counter_by_type["update"] = 0

        stripe_utils = StripeUtils(run_time_args=run_time_args)

        for message in input_messages:
            now = datetime.now()

            if message.type == Type.RECORD:
                record = message.record

                if message.record.data["_valmi_meta"]["_valmi_sync_op"] == "upsert":
                    stripe_utils.upsert(record)
                elif message.record.data["_valmi_meta"]["_valmi_sync_op"] == "update":
                    stripe_utils.update(record)

                counter = counter + 1

                if message.record.data["_valmi_meta"]["_valmi_sync_op"] not in counter_by_type:
                    counter_by_type[message.record.data["_valmi_meta"]["_valmi_sync_op"]] = 0

                counter_by_type[message.record.data["_valmi_meta"]["_valmi_sync_op"]] = (
                    counter_by_type[message.record.data["_valmi_meta"]["_valmi_sync_op"]] + 1
                )

                if counter % run_time_args["chunk_size"] == 0:
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            type=AirbyteStateType.STREAM,
                            data={
                                "records_delivered": counter_by_type,
                                "chunk_id": chunk_id,
                                "finished": False,
                            },
                        ),
                    )
                    if counter % run_time_args["chunk_size"] == 0:
                        counter_by_type.clear()
                        chunk_id = chunk_id + 1

                if (datetime.now() - now).seconds > 5:
                    logger.info("A log every 5 seconds - is this required??")

        # Sync completed - final state message
        yield AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                data={
                    "records_delivered": counter_by_type,
                    "chunk_id": chunk_id,
                    "finished": True,
                },
            ),
        )

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = []
        sinks.append(
            ValmiSink(
                name="Customer",
                id="Customer",
                supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.update],
                json_schema={},
                allow_freeform_fields=True,
                supported_destination_ids_modes=[
                    DestinationIdWithSupportedSyncModes(
                        destination_id="email",
                        destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.update],
                    )
                ],
            )
        )
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            stripe.api_key = config["api_key"]
            value = stripe.Balance.retrieve()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
