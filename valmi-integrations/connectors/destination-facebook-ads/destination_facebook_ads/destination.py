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
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage
from airbyte_cdk.models.airbyte_protocol import Status
from valmi_connector_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
    FieldCatalog,
)
from valmi_connector_lib.common.metrics import get_metric_type
from valmi_connector_lib.valmi_destination import ValmiDestination
from valmi_connector_lib.destination_wrapper.destination_write_wrapper import DestinationWriteWrapper, HandlerResponseData
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.customaudience import CustomAudience

from .fb_ads_utils import FBAdsUtils


class FBAdsWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        self.fb_utils = FBAdsUtils(self.config, self.run_time_args)

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:

        sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]
        metrics = {}
        metrics[get_metric_type(sync_op)] = 0

        flushed, new_metrics, rejected_records = self.fb_utils.add_to_queue(
            counter,
            msg,
            configured_stream=self.configured_catalog.streams[0],
            sink=self.configured_destination_catalog.sinks[0],
        )
        metrics = self.fb_utils.merge_metric_dictionaries(metrics, new_metrics)
        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)

    def finalise_message_handling(self):
        flushed, metrics, rejected_records = self.fb_utils.flush(configured_stream=self.configured_catalog.streams[0], sink=self.configured_destination_catalog.sinks[0])
        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)


class DestinationFacebookAds(ValmiDestination):
    def __init__(self):
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "create", "write"}

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

        fbAds_writer = FBAdsWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return fbAds_writer.start_message_handling(input_messages)

    # TODO: engine support required to support `create` command
    def create(
        self,
        logger: AirbyteLogger,
        config: json,
        object_spec: json,
    ) -> AirbyteConnectionStatus:
        try:
            credentials = config["credentials"]
            FacebookAdsApi.init(credentials["app_id"], credentials["app_secret"],
                                credentials["long_term_acccess_token"], crash_log=False)
            fields = []
            params = {
                "name": f"{object_spec['audience_name']}",
                "subtype": "CUSTOM",
                "description": f"{object_spec['audience_description']}",
                "customer_file_source": "USER_PROVIDED_ONLY",
            }
            my_account = AdAccount(config["account"])

            my_account.create_custom_audience(
                fields=fields,
                params=params,
            )
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        fb_utils = FBAdsUtils(config, None)

        if "account" in config:
            my_account = AdAccount(f'act_{config["account"]}')
            audiences = my_account.get_custom_audiences(fields=["name", "id"])

            sinks = []

            json_schema = fb_utils.get_custom_audience_schema()

            supported_destination_ids = [CustomAudience.Schema.MultiKeySchema.extern_id,
                                         CustomAudience.Schema.MultiKeySchema.email,
                                         CustomAudience.Schema.MultiKeySchema.phone,
                                         CustomAudience.Schema.MultiKeySchema.madid]
            for aud in audiences:
                sinks.append(
                    ValmiSink(
                        label=str(aud["name"]),
                        name=str(aud["id"]),
                        supported_destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
                        field_catalog={
                            DestinationSyncMode.upsert.value: FieldCatalog(
                                json_schema=json_schema,
                                allow_freeform_fields=False,
                                supported_destination_ids=supported_destination_ids,
                            ),
                            DestinationSyncMode.mirror.value: FieldCatalog(
                                json_schema=json_schema,
                                allow_freeform_fields=False,
                                supported_destination_ids=supported_destination_ids,
                            ),
                        },
                    )
                )
            catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=True, object_schema=json_schema)
            catalog.__setattr__("type", "audience")
            catalog.__setattr__("more", False)
            return catalog

        else:
            sinks = []

            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            }
            accounts = list(AdAccountUser(fbid="me").get_ad_accounts(fields=["name", "account_id"]))

            for row in accounts:
                sinks.append(
                    ValmiSink(
                        label=str(row["name"]),
                        name=str(row["account_id"]),
                        supported_destination_sync_modes=(DestinationSyncMode.upsert, DestinationSyncMode.mirror),
                        field_catalog={
                            DestinationSyncMode.upsert.value: FieldCatalog(
                                json_schema=json_schema,
                                allow_freeform_fields=False,
                                supported_destination_ids=[],
                            ),
                            DestinationSyncMode.mirror.value: FieldCatalog(
                                json_schema=json_schema,
                                allow_freeform_fields=False,
                                supported_destination_ids=[],
                            ),
                        },
                    )
                )
            catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=False)
            catalog.__setattr__("type", "account")
            catalog.__setattr__("more", True)
            return catalog

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            credentials = config["credentials"]
            FacebookAdsApi.init(credentials["app_id"], credentials["app_secret"],
                                credentials["long_term_acccess_token"], crash_log=False)

            # checking by getting list of ad accounts
            accounts = list(AdAccountUser(fbid="me").get_ad_accounts(fields=["name", "account_id"]))
            if len(accounts) > 0:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                raise Exception("No ad accounts found")

        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
