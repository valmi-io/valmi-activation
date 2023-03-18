#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
import json
from typing import Any, Dict, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteTraceMessage,
    AirbyteStateMessage,
    TraceType,
    AirbyteErrorTraceMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status, Type, AirbyteStateType
from .custom_http_sink import CustomHttpSink
from valmi_protocol import ValmiDestinationCatalog, ConfiguredValmiDestinationCatalog, ValmiSink
from valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs


class DestinationWebhook(ValmiDestination):
    def __init__(self):
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "write"}

    def write(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiDestinationCatalog,
        input_messages: Iterable[AirbyteMessage],
        state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:
        # TODO: initialise counters from state
        counter = 0

        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

        http_handler = CustomHttpSink(run_time_args=run_time_args)
        for msg in input_messages:
            now = datetime.now()
            if msg.type == Type.RECORD:
                try:
                    http_handler.handle(
                        config, configured_catalog, msg.record.data, counter, run_time_args=run_time_args
                    )
                except Exception as e:
                    yield AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            error=AirbyteErrorTraceMessage(message=str(e)),
                            emitted_at=int(datetime.now().timestamp()) * 1000,
                        ),
                    )
                    return

                counter = counter + 1
                if counter % run_time_args.records_per_metric == 0:
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(
                            type=AirbyteStateType.STREAM,
                            data={
                                "records_delivered": counter,
                                "commit": True if counter % run_time_args.chunk_size == 0 else False,
                            },
                        ),
                    )

                if (datetime.now() - now).seconds > 5:
                    logger.info("A log every 5 seconds - is this required??")

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = [ValmiSink(name="Webhook", supported_sync_modes=["upsert"], json_schema={})]
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            # TODO: What checks make sense for a webhook?
            if not (config["url"].startswith("http://") or config["url"].startswith("https://")):
                raise Exception("invalid url")
            if "headers" in config:
                for header in config["headers"]:
                    kvpair = header.split(":")
                    if len(kvpair) < 2 or len(kvpair[0].strip()) == 0 or len(kvpair[1].strip()) == 0:
                        raise Exception("invalid header - should be of form <key>: <val>")

            # config['method'] validity check already happens in spec verification
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
