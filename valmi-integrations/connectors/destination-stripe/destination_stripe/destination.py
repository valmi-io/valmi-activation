"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Monday, May 1st 2023, 12:30:00 pm
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
from airbyte_cdk.models import AirbyteMessage, Status, AirbyteConnectionStatus
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    ValmiSink,
    FieldCatalog,
)
from valmi_connector_lib.valmi_destination import ValmiDestination
import stripe
from valmi_connector_lib.destination_wrapper.destination_write_wrapper import (
    DestinationWriteWrapper,
    HandlerResponseData,
)
from .stripe_utils import StripeUtils


class StripeWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.stripe_utils = StripeUtils(self.config, self.run_time_args)

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:
        # TODO : handle rejected records and metric type strings.
        metrics = {}
        if msg.record.data["_valmi_meta"]["_valmi_sync_op"] == "upsert":
            obj = self.stripe_utils.upsert(
                msg.record,
                configured_stream=self.configured_catalog.streams[0],
                sink=self.configured_destination_catalog.sinks[0],
            )
            if obj:
                metrics["upsert-ed"] = 1

        elif msg.record.data["_valmi_meta"]["_valmi_sync_op"] == "update":
            obj = self.stripe_utils.update(
                msg.record,
                configured_stream=self.configured_catalog.streams[0],
                sink=self.configured_destination_catalog.sinks[0],
            )
            if obj:
                metrics["updated"] = 1
            else:
                metrics["ignored"] = 1

        return HandlerResponseData(flushed=True, metrics=metrics)

    def finalise_message_handling(self):
        pass


class DestinationStripe(ValmiDestination):
    def __init__(self):
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "write"}

    # TODO: finalise upsert and update methods
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

        stripe_writer = StripeWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return stripe_writer.start_message_handling(input_messages)

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = []
        sinks.append(
            ValmiSink(
                name="Customer",
                id="Customer",
                supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.update],
                field_catalog={
                    DestinationSyncMode.upsert.value: FieldCatalog(
                        json_schema={
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "address": {"type": "object"},
                                "description": {"type": "string"},
                                "email": {"type": "string"},
                                "metadata": {"type": "object"},
                                "name": {"type": "string"},
                                "phone": {"type": "string"},
                                "shipping": {"type": "object"},
                                "balance": {"type": "integer"},
                                "cash_balance": {"type": "object"},
                                "coupon": {"type": "object"},
                                "invoice_prefix": {"type": "string"},
                                "invoice_settings": {"type": "object"},
                                "next_invoice_sequence": {"type": "integer"},
                                "preferred_locales": {"type": "list"},
                                "source": {"type": "object"},
                                "tax": {"type": "object"},
                                "tax_exempt": {"type": "string"},
                                "tax_ids": {"type": "list"},
                                "test_clock": {"type": "string"},
                            },
                        },
                        allow_freeform_fields=True,
                        supported_destination_ids=["email"],
                    ),
                    DestinationSyncMode.update.value: FieldCatalog(
                        json_schema={
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "address": {"type": "object"},
                                "description": {"type": "string"},
                                "email": {"type": "string"},
                                "metadata": {"type": "object"},
                                "name": {"type": "string"},
                                "phone": {"type": "string"},
                                "shipping": {"type": "object"},
                                "payment_method": {"type": "string"},
                                "balance": {"type": "integer"},
                                "cash_balance": {"type": "object"},
                                "coupon": {"type": "object"},
                                "default_source": {"type": "object"},
                                "invoice_prefix": {"type": "string"},
                                "invoice_settings": {"type": "object"},
                                "next_invoice_sequence": {"type": "integer"},
                                "preferred_locales": {"type": "list"},
                                "source": {"type": "object"},
                                "tax": {"type": "object"},
                                "tax_exempt": {"type": "string"},
                            },
                        },
                        allow_freeform_fields=True,
                        supported_destination_ids=["email"],
                    ),
                },
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
