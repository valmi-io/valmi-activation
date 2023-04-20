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
from facebook_business.adobjects.customaudience import CustomAudience


class DestinationFacebookAds(ValmiDestination):
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

    def create(
        self,
        logger: AirbyteLogger,
        config: json,
        object_spec: json,
    ) -> AirbyteConnectionStatus:
        fields = []
        params = {
            "name": "My new Custom Audience",
            "subtype": "CUSTOM",
            "description": "People who purchased on my website",
            "customer_file_source": "USER_PROVIDED_ONLY",
        }
        """
        print(
            type(
                my_account.create_custom_audience(
                    fields=fields,
                    params=params,
                )
            )
        )"""

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        # discover the list of available audiences
        # allow to create a custom one
        sinks = [
            ValmiSink(name="aud1", supported_sync_modes=[DestinationSyncMode.upsert], json_schema={}),
            ValmiSink(name="aud2", supported_sync_modes=[DestinationSyncMode.upsert], json_schema={}),
        ]
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"audience_name": {"type": "string"}},
        }
        return ValmiDestinationCatalog(sinks=sinks, allow_object_creation=True, object_schema=json_schema)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            my_app_id = "241962301579509"
            my_app_secret = "1cf83c3613d6c1fecf04f079780caeed"
            my_access_token = "EAADcED0I4PUBAKEvubsyMM3CQkEBcPGZBY7VztffEfaeZCZCIkdttZBEHaONImNWkEwpkpZAKUVjX4wdZCi5K9bUwyX2Cu6IlnVi7EmE4EUGUZBFCwBughvCdYxQDrW7nBZCZAB8yZAe7NZAZBtVy1L7vJQZBWU3tIvR6NFI81UjRJft8ZBkvPgbEHiVZALrb82blQBcIlfXesCF9Ul3V39CwMRd1NZBBENC03ZB0NaQZD"
            FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)

            # print(list(AdAccountUser(fbid="me").get_ad_accounts(fields=["name", "account_id"])))
            my_account = AdAccount("act_618148706850682")
            print(my_account.get_custom_audiences(fields=["name", "id"]))

            fields = []
            params = {
                "name": "My new Custom Audience",
                "subtype": "CUSTOM",
                "description": "People who purchased on my website",
                "customer_file_source": "USER_PROVIDED_ONLY",
            }
            """
            print(
                type(
                    my_account.create_custom_audience(
                        fields=fields,
                        params=params,
                    )
                )
            )"""
            # Add users

            print(
                CustomAudience("23853634257840489").add_users(
                    schema=[CustomAudience.Schema.MultiKeySchema.email, CustomAudience.Schema.MultiKeySchema.fn],
                    users=[["raj@valmi.io", "Raj V"], ["test@valmi.io", "Test V"]],
                    is_raw=True,
                )
            )

            # DEL USERS
            print(
                CustomAudience("23853634257840489").remove_users(
                    schema=[CustomAudience.Schema.MultiKeySchema.email, CustomAudience.Schema.MultiKeySchema.fn],
                    users=[["raj@valmi.io", "Raj V"], ["test@valmi.io", "Test V"]],
                    is_raw=True,
                )
            )

            # ADD USERS
            print(
                CustomAudience("23853634257840489").add_users(
                    schema=[CustomAudience.Schema.MultiKeySchema.email, CustomAudience.Schema.MultiKeySchema.fn],
                    users=[["v.rajashekar@gmail.com", "Raj V"]],
                    is_raw=True,
                )
            )

            # write facebook marketing api code to add users to custom audience here

            """
            my_account = AdAccount("act_{{adaccount-id}}")
            campaigns = my_account.get_campaigns()
            print(campaigns)
            """
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
