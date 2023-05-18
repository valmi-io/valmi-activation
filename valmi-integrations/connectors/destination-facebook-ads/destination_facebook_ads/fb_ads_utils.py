from typing import Any, Mapping
from airbyte_cdk import AirbyteLogger
from valmi_connector_lib.valmi_protocol import (
    ValmiStream,
    ConfiguredValmiSink,
    DestinationSyncMode,
    DestinationIdWithSupportedSyncModes,
)
from .run_time_args import RunTimeArgs
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.api import FacebookAdsApi


class FBAdsUtils:
    max_records = 1000
    logger = AirbyteLogger()

    def __init__(self, config: Mapping[str, Any], run_time_args: RunTimeArgs, *args, **kwargs):
        FacebookAdsApi.init(config["app_id"], config["app_secret"], config["long_term_acccess_token"])

        self.users = []
        self.schema = None
        self.lookup_keys = None
        self.is_deleting = True

    def get_custom_audience_schema(self):
        key_types = [
            CustomAudience.Schema.MultiKeySchema.extern_id,
            CustomAudience.Schema.MultiKeySchema.email,
            CustomAudience.Schema.MultiKeySchema.phone,
            CustomAudience.Schema.MultiKeySchema.gen,
            CustomAudience.Schema.MultiKeySchema.doby,
            CustomAudience.Schema.MultiKeySchema.dobm,
            CustomAudience.Schema.MultiKeySchema.dobd,
            CustomAudience.Schema.MultiKeySchema.ln,
            CustomAudience.Schema.MultiKeySchema.fn,
            CustomAudience.Schema.MultiKeySchema.fi,
            CustomAudience.Schema.MultiKeySchema.ct,
            CustomAudience.Schema.MultiKeySchema.st,
            CustomAudience.Schema.MultiKeySchema.zip,
            CustomAudience.Schema.MultiKeySchema.madid,
            CustomAudience.Schema.MultiKeySchema.country,
            CustomAudience.Schema.MultiKeySchema.appuid,
        ]

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {key_type: {"type": "string"} for key_type in key_types},
        }

    def get_id_keys_with_supported_sync_modes(self):
        key_types = [
            DestinationIdWithSupportedSyncModes(
                destination_id=CustomAudience.Schema.MultiKeySchema.extern_id,
                destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
            ),
            DestinationIdWithSupportedSyncModes(
                destination_id=CustomAudience.Schema.MultiKeySchema.email,
                destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
            ),
            DestinationIdWithSupportedSyncModes(
                destination_id=CustomAudience.Schema.MultiKeySchema.phone,
                destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
            ),
            DestinationIdWithSupportedSyncModes(
                destination_id=CustomAudience.Schema.MultiKeySchema.madid,
                destination_sync_modes=[DestinationSyncMode.upsert, DestinationSyncMode.mirror],
            ),
        ]

        return key_types

    def add_to_queue(self, data, configured_stream: ValmiStream, sink: ConfiguredValmiSink) -> bool:
        if data["_valmi_meta"]["_valmi_sync_op"] == "delete":
            self.users.append([data[configured_stream.id_key]])
            if len(self.users) >= self.max_records:
                self.flush(configured_stream, sink)

        else:
            # Upsert mode
            if self.is_deleting:
                self.flush(configured_stream, sink)

            # initialise schema and lookup_keys only once
            if self.schema is None:
                self.schema = [sink.destination_id]
                self.lookup_keys = [configured_stream.id_key]

                for k, v in sink.mapping.items():
                    self.schema.extend(v)
                    self.lookup_keys.extend(k)

            self.users.append([data[key] for key in self.lookup_keys])
            if len(self.users) >= self.max_records:
                self.flush(configured_stream, sink)

    def flush(self, configured_stream: ValmiStream, sink: ConfiguredValmiSink):
        if self.is_deleting:
            if len(self.users) > 0:
                CustomAudience(sink.sink.id).remove_users(
                    schema=[sink.destination_id],
                    users=[self.users],
                    is_raw=True,
                )
            self.is_deleting = False
            self.users.clear()
        else:
            CustomAudience(sink.sink.id).add_users(
                schema=self.schema,
                users=self.users,
                is_raw=True,
            )
            self.users.clear()
