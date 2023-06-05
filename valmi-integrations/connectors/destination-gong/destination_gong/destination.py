"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, May 18th 2023, 7:42:43 pm
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
    AirbyteMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status
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
from valmi_connector_lib.common.metrics import get_metric_type
from valmi_connector_lib.valmi_destination import ValmiDestination
import requests
from .gong_utils import BASE_API_URL, GongUtils


class GongWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.gong_utils = GongUtils(
            self.config,
            self.configured_destination_catalog.sinks[0],
            self.run_time_args,
        )

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:
        metrics = {}
        sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]

        rejected_records = []
        if sync_op == "upsert":
            sync_op_response = self.gong_utils.upsert(
                msg.record,
                configured_stream=self.configured_catalog.streams[0],
                sink=self.configured_destination_catalog.sinks[0],
            )
            if sync_op_response.rejected:
                metrics[get_metric_type("reject")] = 1
                rejected_records.append(sync_op_response.rejected_record)
            else:
                metrics[get_metric_type(sync_op)] = 1

        elif sync_op == "update":
            sync_op_response = self.gong_utils.update(
                msg.record,
                configured_stream=self.configured_catalog.streams[0],
                sink=self.configured_destination_catalog.sinks[0],
            )
            if sync_op_response.rejected:
                metrics[get_metric_type("reject")] = 1
                rejected_records.append(sync_op_response.rejected_record)
            elif sync_op_response.obj:
                metrics[get_metric_type(sync_op)] = 1
            else:
                metrics[get_metric_type("ignore")] = 1

        return HandlerResponseData(flushed=True, metrics=metrics, rejected_records=rejected_records)

    def finalise_message_handling(self):
        pass


class DestinationGong(ValmiDestination):
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
        gong_writer = GongWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return gong_writer.start_message_handling(input_messages)

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        if "integrationId" in config:
            sinks = []
            basic_field_catalog = FieldCatalog(
                json_schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "objectId": {"type": "string", "description": "The CRM unique ID for the object"},
                        "modifiedDate": {
                            "type": "string",
                            "description": "The date and time the object was last modified in the CRM. ISO-8601 datetime format, without milliseconds.",
                        },
                        "isDeleted": {
                            "type": "boolean",
                            "description": "(Default: false) When true, the object is deleted from the database",
                        },
                        "url": {"type": "string", "description": "A full http URL to browse this object in the CRM"},
                        "emailAddress": {
                            "type": "string",
                            "description": "The lead's email address. Used to associate activities to a lead, based on the participants email.",
                        },
                        "firstName": {"type": "string", "description": "The lead's first name."},
                        "lastName": {"type": "string", "description": "The lead's last name."},
                        "title": {"type": "string", "description": "The lead's title."},
                        "phoneNumber": {
                            "type": "string",
                            "description": "The lead's phone number. Used to associated telephony system calls to a lead based on the call participant's phone number.",
                        },
                        "convertedToDealId": {
                            "type": "string",
                            "description": "The deal ID in the CRM. Relevant if the lead is converted to a deal",
                        },
                        "convertedToContactId": {
                            "type": "string",
                            "description": "The contact ID in the CRM the lead was converted to. Relevant if the lead is converted to a contact",
                        },
                        "convertedToAccountId": {
                            "type": "string",
                            "description": "The account ID in the CRM the lead was converted to. Relevant if the lead is converted to an account",
                        },
                    },
                },
                allow_freeform_fields=True,
                supported_destination_ids=["objectId"],
                mandatory_fields=["objectId", "modifiedDate"],
            )

            account_field_catalog = FieldCatalog(
                json_schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "objectId": {"type": "string", "description": "The CRM unique ID for the object"},
                        "modifiedDate": {
                            "type": "string",
                            "description": "The date and time the object was last modified in the CRM. ISO-8601 datetime format, without milliseconds.",
                        },
                        "isDeleted": {
                            "type": "boolean",
                            "description": "(Default: false) When true, the object is deleted from the database",
                        },
                        "url": {"type": "string", "description": "A full http URL to browse this object in the CRM"},
                        "name": {
                            "type": "string",
                            "description": 'Default value: "Account_#"+objectId',
                        },
                        "domains": {
                            "type": "list[array]",
                            "description": "The account's domain/s. When an activity can’t be associated with a contact, the participants domain is used to associate the activity to an account via the account domain in this field.",
                        },
                    },
                },
                allow_freeform_fields=True,
                supported_destination_ids=["objectId"],
                mandatory_fields=["objectId", "modifiedDate"],
            )

            business_user_catalog = FieldCatalog(
                json_schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "objectId": {"type": "string", "description": "The CRM unique ID for the object"},
                        "modifiedDate": {
                            "type": "string",
                            "description": "The date and time the object was last modified in the CRM. ISO-8601 datetime format, without milliseconds.",
                        },
                        "isDeleted": {
                            "type": "boolean",
                            "description": "(Default: false) When true, the object is deleted from the database",
                        },
                        "url": {"type": "string", "description": "A full http URL to browse this object in the CRM"},
                        "emailAddress": {
                            "type": "string",
                            "description": "The business user's email address. Used to associate the Gong user with the CRM user. Not mandatory when isDeleted = true.",
                        },
                    },
                },
                allow_freeform_fields=True,
                supported_destination_ids=["objectId"],
                mandatory_fields=["objectId", "modifiedDate", "emailAddress"],
            )

            deal_catalog = FieldCatalog(
                json_schema={
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "objectId": {"type": "string", "description": "The CRM unique ID for the object"},
                        "modifiedDate": {
                            "type": "string",
                            "description": "The date and time the object was last modified in the CRM. ISO-8601 datetime format, without milliseconds.",
                        },
                        "isDeleted": {
                            "type": "boolean",
                            "description": "(Default: false) When true, the object is deleted from the database",
                        },
                        "url": {"type": "string", "description": "A full http URL to browse this object in the CRM"},
                        "accountId": {
                            "type": "string",
                            "description": "The ID of the account the deal is associated with in the CRM. Note: Deals without an accountId will not appear in Gong",
                        },
                        "ownerId": {
                            "type": "string",
                            "description": "The ID of the deal owner in the CRM. This ID should be the same as the business user objectId so the deal can be associated with the correct Gong user. Note: Deals without an ownerId will not appear in the deal board in Gong.",
                        },
                        "name": {
                            "type": "string",
                            "description": "The deal name Default value: Deal_# + objectId",
                        },
                        "createdDate": {
                            "type": "string",
                            "description": "The date and time the deal was created in the CRM.",
                        },
                        "closeDate": {
                            "type": "string",
                            "description": "The date the deal closed or is expected to close. Note: Deals without a closeDate will not appear in the deal board in Gong.",
                        },
                        "status": {
                            "type": "string",
                            "description": """The deal status. Possible values are:
WON
LOST
OPEN

Default value: OPEN""",
                        },
                        "stage": {
                            "type": "string",
                            "description": "The stage the deal is in. If empty, it will not always be possible to associate activities with deals. Must be the same as one of the values in the objectId field in the stages object",
                        },
                        "amount": {
                            "type": "number",
                            "description": """The deal amount in the currency unit. Companies set their default currency in the Company Settings page. All amounts should be sent in this currency. If your deal is in a different currency, convert the deal amount to the currency defined in the Company Settings page.
Default value: 0""",
                        },
                    },
                },
                allow_freeform_fields=True,
                supported_destination_ids=["objectId"],
                mandatory_fields=["objectId", "modifiedDate"],
            )
            sinks.extend(
                [
                    ValmiSink(
                        name="LEAD",
                        label="Lead",
                        supported_destination_sync_modes=[
                            DestinationSyncMode.upsert,
                            DestinationSyncMode.update,
                        ],
                        field_catalog={
                            DestinationSyncMode.upsert.value: basic_field_catalog,
                            DestinationSyncMode.update.value: basic_field_catalog,
                        },
                        integrationId=config["integrationId"],
                    ),
                    ValmiSink(
                        name="ACCOUNT",
                        label="Account",
                        supported_destination_sync_modes=[
                            DestinationSyncMode.upsert,
                            DestinationSyncMode.update,
                        ],
                        field_catalog={
                            DestinationSyncMode.upsert.value: account_field_catalog,
                            DestinationSyncMode.update.value: account_field_catalog,
                        },
                        integrationId=config["integrationId"],
                    ),
                    ValmiSink(
                        name="BUSINESS_USER",
                        label="Business User",
                        supported_destination_sync_modes=[
                            DestinationSyncMode.upsert,
                            DestinationSyncMode.update,
                        ],
                        field_catalog={
                            DestinationSyncMode.upsert.value: business_user_catalog,
                            DestinationSyncMode.update.value: business_user_catalog,
                        },
                        integrationId=config["integrationId"],
                    ),
                    ValmiSink(
                        name="DEAL",
                        label="Deal",
                        supported_destination_sync_modes=[
                            DestinationSyncMode.upsert,
                            DestinationSyncMode.update,
                        ],
                        field_catalog={
                            DestinationSyncMode.upsert.value: deal_catalog,
                            DestinationSyncMode.update.value: deal_catalog,
                        },
                        integrationId=config["integrationId"],
                    ),
                ]
            )
            return ValmiDestinationCatalog(sinks=sinks)

        else:
            sinks = []
            access_key = config["access_key"]
            access_key_secret = config["access_key_secret"]
            resp = requests.get(f"{BASE_API_URL}/v2/crm/integrations", auth=(access_key, access_key_secret))

            # Checking for integrations list. Can specifically check for CRM integration, not doing so now.
            if resp.status_code == 200 and len(resp.json()["integrations"]) > 0:
                crm = resp.json()["integrations"][0]
                sinks.append(
                    ValmiSink(
                        name=crm["integrationId"],
                        label=crm["name"],
                        supported_destination_sync_modes=[DestinationSyncMode.upsert],  # Dummy
                        field_catalog={},
                    )
                )
            else:
                raise Exception(
                    "Getting CRM API integrations failed. Please check if a Generic CRM is intgerated with Gong."
                )

            catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=False)
            catalog.__setattr__("type", "integrationId")
            catalog.__setattr__("more", True)
            return catalog

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            access_key = config["access_key"]
            access_key_secret = config["access_key_secret"]
            resp = requests.get(f"{BASE_API_URL}/v2/crm/integrations", auth=(access_key, access_key_secret))

            # Checking for integrations list. Can specifically check for CRM integration, not doing so now.
            if resp.status_code == 200 and len(resp.json()["integrations"]) > 0:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message="Checking for CRM API integration failed. Please check if a Generic CRM is intgerated with Gong.",
                )
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
