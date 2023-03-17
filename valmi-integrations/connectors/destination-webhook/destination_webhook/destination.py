#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Iterable, Mapping
from urllib.parse import quote, urlencode

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status, Type
from valmi_protocol import ValmiDestination, ValmiDestinationCatalog, ConfiguredValmiDestinationCatalog


class DestinationWebhook(ValmiDestination):
    def __init__(self):
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "write"}

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiDestinationCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """
        TODO
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        for msg in input_messages:
            # print(msg.json(exclude_none=True))
            if msg.type == Type.RECORD:
                # construct props
                # print(msg)
                props = {}
                for prop in msg.record.data:
                    props[prop] = msg.record.data[prop]

                r = requests.get(f"{config['url']}/{msg.record.stream}?{ urlencode(props, quote_via=quote)}")

                # print(r.json())

            # print(msg.json(exclude_none=True))

        out_record = AirbyteStateMessage(data={"checkpoint": "checkpoint"})
        out_message = AirbyteMessage(type=Type.STATE, state=out_record)
        yield out_message

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = []
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            # TODO

            # print("checking")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
