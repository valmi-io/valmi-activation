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
from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteStateMessage,
    AirbyteMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status, Type, AirbyteStateType
from valmi_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
)
from valmi_lib.valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs

from customerio import Regions
from datetime import datetime

from .customer_io_utils import CustomerIOExt, get_region


class DestinationCustomerIO(ValmiDestination):
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
        counter = 0
        chunk_id = 0
        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

        cio = CustomerIOExt(
            run_time_args,
            config["tracking_site_id"],
            config["tracking_api_key"],
            region=Regions.US
            if get_region(config["tracking_site_id"], config["tracking_api_key"]).lower() == "us"
            else Regions.EU,
            url_prefix="/api/v2",
        )
        for message in input_messages:
            now = datetime.now()

            if message.type == Type.RECORD:
                record = message.record
                flushed = cio.add_to_queue(
                    record.data,
                    configured_stream=configured_catalog.streams[0],
                    sink=configured_destination_catalog.sinks[0],
                )

                counter = counter + 1
                if flushed or counter % run_time_args["chunk_size"] == 0:
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            type=AirbyteStateType.STREAM,
                            data={
                                "records_delivered": {DestinationSyncMode.upsert: counter},
                                "chunk_id": chunk_id,
                                "finished": False,
                            },
                        ),
                    )
                    chunk_id = chunk_id + 1

                if (datetime.now() - now).seconds > 5:
                    logger.info("A log every 5 seconds - is this required??")

        cio.flush()
        # Sync completed - final state message
        yield AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                data={
                    "records_delivered": {DestinationSyncMode.upsert: counter},
                    "chunk_id": chunk_id,
                    "finished": True,
                },
            ),
        )

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = [
            ValmiSink(name="Person", supported_sync_modes=[DestinationSyncMode.upsert], json_schema={}),
            ValmiSink(name="Device", supported_sync_modes=[DestinationSyncMode.upsert], json_schema={}),
        ]
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            cio = CustomerIOExt(
                config["tracking_site_id"],
                config["tracking_api_key"],
                region=Regions.US
                if get_region(config["tracking_site_id"], config["tracking_api_key"]).lower() == "us"
                else Regions.EU,
            )
            cio.identify(
                id="connector-test@valmi.io", email="connector-test@valmi.io", name="test.valmi.io", plan="free"
            )
            cio.delete(customer_id="connector-test@valmi.io")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")