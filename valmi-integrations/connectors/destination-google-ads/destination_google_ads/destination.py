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
from typing import Any, Iterable, Mapping, Dict

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteStateType,
    Type,
    AirbyteConnectionStatus,
    AirbyteStateMessage,
    AirbyteMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    FieldCatalog,
)
from valmi_connector_lib.valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs

from google.auth.exceptions import RefreshError
from google.ads.googleads.client import GoogleAdsClient

from .client import GoogleClient
from .google_ads_utils import GoogleAdsUtils
from .google_ads_account import GoogleAdsAccount
from valmi_connector_lib.destination_wrapper.destination_write_wrapper \
    import DestinationWriteWrapper, HandlerResponseData


class GoogleAdsWriter(DestinationWriteWrapper):
    def initialise_message_handling(self) -> None:
        # Get manager account id if there is one
        manager_id = self.configured_destination_catalog.sinks[0].sink.__dict__.get("manager_id", "None")
        if manager_id == "None":
            manager_id = None

        google_client: GoogleAdsClient = GoogleClient(self.config).authorize(manager_id)
        self.google_ads_utils = GoogleAdsUtils(self.logger, google_client, self.run_time_args)

    def handle_message(self, msg: AirbyteMessage, counter: int) -> HandlerResponseData:
        flushed = self.google_ads_utils.add_to_queue(
            msg.record.data,
            configured_stream=self.configured_catalog.streams[0],
            sink=self.configured_destination_catalog.sinks[0]
        )

        return HandlerResponseData(flushed=flushed)

    def finalise_message_handling(self) -> None:
        self.google_ads_utils.flush(sink=self.configured_destination_catalog.sinks[0])
        self.google_ads_utils.submit_offline_jobs(sink=self.configured_destination_catalog.sinks[0])


class DestinationGoogleAds(ValmiDestination):
    def __init__(self) -> None:
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "write", "create"}

    def write(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiCatalog,
        configured_destination_catalog: ConfiguredValmiDestinationCatalog,
        input_messages: Iterable[AirbyteMessage],
        # state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:

        google_ads_writer = GoogleAdsWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return google_ads_writer.start_message_handling(input_messages)

    def create(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        object_spec: Mapping[str, Any],
    ) -> AirbyteConnectionStatus:

        # ToDo: Complete this method and test it
        try:
            account_info = json.loads(str(config.get("account")))
            google_client: GoogleAdsClient = GoogleClient(config).\
                authorize(account_info.get("manager", None))
            google_ads_utils = GoogleAdsUtils(logger, google_client)
            google_ads_account = GoogleAdsAccount(logger, google_client, str(account_info.get("account")))

            user_list_resource_name = google_ads_account.create_customer_match_user_list(
                name=f"{object_spec['audience_name']}",
                description=f"{object_spec['audience_description']}",
                membership_life_span=int(object_spec['membership_life_span']),
            )

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> ValmiDestinationCatalog:

        logger.info(config.get("account"))
        account_info: Dict[str, str] = {}
        if "account" in config:
            account_info = json.loads(str(config.get("account")))
            
        manager_id = account_info.get("manager", None)
        google_client: GoogleAdsClient = GoogleClient(config).authorize(manager_id)
        google_ads_utils = GoogleAdsUtils(logger, google_client)

        if "account" in config:
            google_ads_account = GoogleAdsAccount(logger, google_client, str(account_info.get("account")))
            audiences = google_ads_account.get_custom_audiences()

            sinks = []
            json_schema = google_ads_utils.get_custom_audience_schema()

            for aud in audiences:
                sinks.append(
                    ValmiSink(
                        label=str(aud.name),
                        name=str(aud.resource_name),
                        manager_id=str(manager_id),
                        supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
                        field_catalog={
                            DestinationSyncMode.upsert.value: FieldCatalog(
                                json_schema=json_schema,
                                allow_freeform_fields=False,
                                supported_destination_ids=["email"]
                            ),
                            DestinationSyncMode.mirror.value: FieldCatalog(
                                json_schema=json_schema,
                                allow_freeform_fields=False,
                                supported_destination_ids=["email"]
                            ),
                        }
                    )
                )
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "audience_name": {"type": "string"}, 
                    "audience_description": {"type": "string"},
                    "membership_life_span": {"type": "int"}
                },
            }
            catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=True, object_schema=json_schema)
            catalog.__setattr__("type", "audience")
            catalog.__setattr__("more", False)
            return catalog

        else:
            sinks = []
            accounts = google_ads_utils.get_accounts()

            for account_info in accounts:

                # We dont want null as manager id
                if account_info["manager"] is None:
                    account_info.pop("manager")

                sinks.append(
                    ValmiSink(
                        name=str(json.dumps(account_info)),
                        label=str(account_info["account"]),
                        supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
                        field_catalog={}
                    )
                )
            catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=False)
            catalog.__setattr__("type", "account")
            catalog.__setattr__("more", True)
            return catalog

        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Connection check method for Google Ads.
        Info:
            Checks whether target spreadsheet_id is available using provided credentials.
        Returns:
            :: Status.SUCCEEDED - if creadentials are valid, token is refreshed, target spreadsheet is available.
            :: Status.FAILED - if could not obtain new token, target spreadsheet is not available or other exception occured (with message).
        """
        logger.info("Checking connection...")
        logger.info(config)
        try:
            client = GoogleClient(config).authorize()

            # Get customer ids to check if credentials are valid
            customer_service = client.get_service("CustomerService")

            accessible_customers = customer_service.list_accessible_customers()
            result_total = len(accessible_customers.resource_names)

            if result_total == 0:
                return AirbyteConnectionStatus(status=Status.FAILED, message="No accessible customers found")
            else:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except RefreshError as token_err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{token_err}")
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
