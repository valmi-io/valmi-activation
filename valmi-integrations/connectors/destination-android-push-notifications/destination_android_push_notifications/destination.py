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
import firebase_admin

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
from valmi_connector_lib.destination_wrapper.destination_write_wrapper import \
    DestinationWriteWrapper, HandlerResponseData

from firebase_admin import credentials
from .fcm_utils import FCMUtils


class FCMWriter(DestinationWriteWrapper):
    def initialise_message_handling(self):
        title_template = self.configured_destination_catalog.sinks[0].template_fields["title"]
        body_template = self.configured_destination_catalog.sinks[0].template_fields["message"]
        mapping = self.configured_destination_catalog.sinks[0].mapping

        self.fcm_utils = FCMUtils(
            self.config,
            self.run_time_args,
            title_template=title_template,
            body_template=body_template,
            field_mapping=mapping,
        )

    def handle_message(
        self,
        msg,
        counter,
    ) -> HandlerResponseData:

        sync_op = msg.record.data["_valmi_meta"]["_valmi_sync_op"]
        metrics = {}
        metrics[get_metric_type(sync_op)] = 0

        flushed, new_metrics, rejected_records = self.fcm_utils.add_to_queue(
            counter,
            msg,
            configured_stream=self.configured_catalog.streams[0],
            sink=self.configured_destination_catalog.sinks[0],
        )
        metrics = self.fcm_utils.merge_metric_dictionaries(metrics, new_metrics)
        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)

    def finalise_message_handling(self):
        flushed, metrics, rejected_records = self.fcm_utils.flush(
            configured_stream=self.configured_catalog.streams[0],
            sink=self.configured_destination_catalog.sinks[0]
        )
        return HandlerResponseData(flushed=flushed, metrics=metrics, rejected_records=rejected_records)


class DestinationAndroidPushNotifications(ValmiDestination):
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
        fcm_writer = FCMWriter(logger, config, configured_catalog, configured_destination_catalog, None)
        return fcm_writer.start_message_handling(input_messages)

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        fcm_utils = FCMUtils(config, None)
        json_schema = fcm_utils.get_cloud_messaging_schema()
        sinks = []

        basic_field_catalog = FieldCatalog(
            json_schema=json_schema,
            allow_freeform_fields=True,
            supported_destination_ids=[],
            mandatory_fields=["device_id"],
            template_fields={
                "title": {
                    "type": "string",
                    "label": "Title",
                    "description": "Notification title. You can use jinja template with the mapped fields to format the message. For example: `{{title}}` will be replaced with the value of the `title` field. So you can write '{{title}}, ...'",
                    "required": True
                },
                "message": {
                    "type": "string",
                    "label": "Message",
                    "description": "Message to be sent to the channel. You can use jinja template with the mapped fields to format the message. For example: `{{message}}` will be replaced with the value of the `message` field. So you can write 'check out '{{message}}'",
                    "required": True
                }
            },
        )

        sinks.append(
            ValmiSink(
                label=str("Firebase Cloud Messaging"),
                name=str(fcm_utils.app.project_id),
                supported_destination_sync_modes=[
                    DestinationSyncMode.upsert,
                    DestinationSyncMode.update,
                    DestinationSyncMode.create,
                    DestinationSyncMode.append
                ],
                field_catalog={
                    DestinationSyncMode.upsert.value: basic_field_catalog,
                    DestinationSyncMode.update.value: basic_field_catalog,
                    DestinationSyncMode.create.value: basic_field_catalog,
                    DestinationSyncMode.append.value: basic_field_catalog
                },
            )
        )

        catalog = ValmiDestinationCatalog(sinks=sinks, allow_object_creation=False, object_schema=json_schema)
        catalog.__setattr__("type", "audience")
        catalog.__setattr__("more", False)
        return catalog

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            service_ac_credentials_str = config["service_account"]
            service_ac_credentials = json.loads(service_ac_credentials_str)
            creds = credentials.Certificate(service_ac_credentials)
            firebase_admin.initialize_app(creds)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
