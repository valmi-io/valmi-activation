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
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteStateMessage, AirbyteMessage
from airbyte_cdk.models.airbyte_protocol import Type, AirbyteStateType, Status
from valmi_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ValmiSink,
    ConfiguredValmiCatalog,
    ConfiguredValmiDestinationCatalog,
    DestinationSyncMode,
)
from valmi_lib.valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs

from datetime import datetime
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser

from .fb_ads_utils import FBAdsUtils


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
        counter = 0
        counter_by_type = {}
        chunk_id = 0
        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

        counter_by_type["upsert"] = 0
        counter_by_type["delete"] = 0

        fb_utils = FBAdsUtils(config, None)

        # It is assumed and required that all deletes are done before upserts
        for message in input_messages:
            now = datetime.now()

            if message.type == Type.RECORD:
                record = message.record
                flushed = fb_utils.add_to_queue(
                    record.data,
                    configured_stream=configured_catalog.streams[0],
                    sink=configured_destination_catalog.sinks[0],
                )

                counter = counter + 1

                if message.record.data["_valmi_meta"]["_valmi_sync_op"] not in counter_by_type:
                    counter_by_type[message.record.data["_valmi_meta"]["_valmi_sync_op"]] = 0

                counter_by_type[message.record.data["_valmi_meta"]["_valmi_sync_op"]] = (
                    counter_by_type[message.record.data["_valmi_meta"]["_valmi_sync_op"]] + 1
                )

                if flushed or counter % run_time_args["chunk_size"] == 0:
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

        fb_utils.flush(configured_stream=configured_catalog.streams[0], sink=configured_destination_catalog.sinks[0])
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

    def create(
        self,
        logger: AirbyteLogger,
        config: json,
        object_spec: json,
    ) -> AirbyteConnectionStatus:
        try:
            FacebookAdsApi.init(config["app_id"], config["app_secret"], config["long_term_acccess_token"])

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
            my_account = AdAccount(config["account"])
            audiences = my_account.get_custom_audiences(fields=["name", "id"])

            sinks = []

            json_schema = fb_utils.get_custom_audience_schema()

            for aud in audiences:
                sinks.append(
                    ValmiSink(
                        name=str(aud["name"]),
                        id=str(aud["id"]),
                        supported_destination_sync_modes=(DestinationSyncMode.upsert, DestinationSyncMode.mirror),
                        json_schema=json_schema,
                        supported_destination_ids_modes=fb_utils.get_id_keys_with_supported_sync_modes(),
                        allow_freeform_fields=False,
                    )
                )
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {"audience_name": {"type": "string"}, "audience_description": {"type": "string"}},
            }
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
                        name=str(row["name"]),
                        id=str(row["account_id"]),
                        supported_destination_sync_modes=(DestinationSyncMode.upsert, DestinationSyncMode.mirror),
                        # json_schema=json_schema,
                        allow_freeform_fields=False,
                    )
                )
            catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=False)
            catalog.__setattr__("type", "account")
            catalog.__setattr__("more", True)
            return catalog

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            FacebookAdsApi.init(config["app_id"], config["app_secret"], config["long_term_acccess_token"])

            # checking by getting list of ad accounts
            accounts = list(AdAccountUser(fbid="me").get_ad_accounts(fields=["name", "account_id"]))
            if len(accounts) > 0:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                raise Exception("No ad accounts found")

        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
