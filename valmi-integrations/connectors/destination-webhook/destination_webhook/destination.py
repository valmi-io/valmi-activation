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


from datetime import datetime
import json
from typing import Any, Iterable, Mapping
import socket
from contextlib import closing
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
from valmi_lib.valmi_protocol import (
    ValmiDestinationCatalog,
    ConfiguredValmiDestinationCatalog,
    ConfiguredValmiCatalog,
    ValmiSink,
    DestinationSyncMode,
    FieldCatalog,
)
from valmi_lib.valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs
from urllib.parse import urlparse


class DestinationWebhook(ValmiDestination):
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
        counter_by_type = {}
        chunk_id = 0

        # REORGANIZE THIS - initialising metrics
        counter_by_type["upsert"] = 0
        counter_by_type["delete"] = 0

        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})

        http_handler = CustomHttpSink(run_time_args=run_time_args)
        for msg in input_messages:
            now = datetime.now()
            if msg.type == Type.RECORD:
                try:
                    http_handler.handle(
                        config, configured_destination_catalog, msg.record.data, counter, run_time_args=run_time_args
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

                if msg.record.data["_valmi_meta"]["_valmi_sync_op"] not in counter_by_type:
                    counter_by_type[msg.record.data["_valmi_meta"]["_valmi_sync_op"]] = 0

                counter_by_type[msg.record.data["_valmi_meta"]["_valmi_sync_op"]] = (
                    counter_by_type[msg.record.data["_valmi_meta"]["_valmi_sync_op"]] + 1
                )

                if counter % run_time_args.records_per_metric == 0 or counter % run_time_args.chunk_size == 0:
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
                    if counter % run_time_args.chunk_size == 0:
                        counter_by_type.clear()
                        chunk_id = chunk_id + 1

                if (datetime.now() - now).seconds > 5:
                    logger.info("A log every 5 seconds - is this required??")

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

    # TODO: may not need to do supported_destination_ids_modes , check with UI
    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = []
        basic_field_catalog = FieldCatalog(
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            },
            allow_freeform_fields=True,
            supported_destination_ids=[],
        )
        sinks.append(
            ValmiSink(
                name="Webhook",
                id="Webhook",
                supported_destination_sync_modes=[
                    DestinationSyncMode.upsert,
                    DestinationSyncMode.mirror,
                    DestinationSyncMode.append,
                    DestinationSyncMode.update,
                    DestinationSyncMode.create,
                ],
                field_catalog={
                    DestinationSyncMode.append.value: basic_field_catalog,
                    DestinationSyncMode.mirror.value: basic_field_catalog,
                    DestinationSyncMode.append.value: basic_field_catalog,
                    DestinationSyncMode.update.value: basic_field_catalog,
                    DestinationSyncMode.create.value: basic_field_catalog,
                },
            )
        )
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            if not (config["url"].startswith("http://") or config["url"].startswith("https://")):
                raise Exception("invalid url")
            if "headers" in config:
                for header in config["headers"]:
                    kvpair = header.split(":")
                    if len(kvpair) < 2 or len(kvpair[0].strip()) == 0 or len(kvpair[1].strip()) == 0:
                        raise Exception("invalid header - should be of form <key>: <val>")

            # TODO: What checks make sense for a webhook? Currently just checking for port open
            url = config["url"]
            parsed = urlparse(url)
            scheme = parsed.scheme if parsed.scheme else "http"
            port = parsed.port if parsed.port else 80 if scheme == "http" else 443
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex((parsed.hostname, port)) == 0:
                    return AirbyteConnectionStatus(status=Status.SUCCEEDED)
                else:
                    return AirbyteConnectionStatus(status=Status.FAILED, message=f"Port {port} is not open")
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
