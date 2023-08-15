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

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    FieldCatalog
)
from valmi_connector_lib.valmi_destination import ValmiDestination

from customerio import Regions
from valmi_connector_lib.destination_wrapper.destination_write_wrapper import DestinationWriteWrapper, HandlerResponseData
from .customer_io_utils import CustomerIOExt, get_region


class CustomerIOWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.cio = CustomerIOExt(
            self.run_time_args,
            self.config["tracking_site_id"],
            self.config["tracking_api_key"],
            region=Regions.US
            if get_region(self.config["tracking_site_id"], self.config["tracking_api_key"]).lower() == "us"
            else Regions.EU,
            url_prefix="/api/v2",
        )
        
    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:
        flushed, metrics, rejected_records = self.cio.add_to_queue(counter, msg, configured_stream=self.configured_catalog.streams[0], sink=self.configured_destination_catalog.sinks[0])
        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)
    
    def finalise_message_handling(self) -> HandlerResponseData:
        sync_op = self.configured_destination_catalog.sinks[0].destination_sync_mode.value

        metrics, rejected_records = self.cio.flush(sync_op)
        return HandlerResponseData(flushed=True, metrics=metrics, rejected_records=rejected_records)


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
        state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:

        customer_io_writer = CustomerIOWriter(logger, config, configured_catalog, configured_destination_catalog, state)
        return customer_io_writer.start_message_handling(input_messages)
 
    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:

        sinks = []
        sinks.append(
            ValmiSink(
                name="Person",
                label="Person",
                supported_destination_sync_modes=[DestinationSyncMode.upsert],
                field_catalog={
                    DestinationSyncMode.upsert.value: FieldCatalog(
                        json_schema={
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "email": {"type": "string"},
                                "cio_id": {"type": "string"},
                            },
                        },
                        allow_freeform_fields=True,
                        supported_destination_ids=["id", "email", "cio_id"],
                    )
                },
            )
        )
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            logger.debug(get_region(config["tracking_site_id"], config["tracking_api_key"]))
            cio = CustomerIOExt(
                run_time_args=None,     
                site_id=config["tracking_site_id"],
                api_key=config["tracking_api_key"],
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
