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
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
)
from airbyte_cdk.models.airbyte_protocol import Status
from valmi_protocol import ValmiDestinationCatalog, ConfiguredValmiDestinationCatalog, ValmiSink
from valmi_destination import ValmiDestination
from .run_time_args import RunTimeArgs

from google.auth.exceptions import RefreshError

from .client import GoogleSheetsClient
from .helpers import ConnectionTest, get_spreadsheet_id
from .spreadsheet import GoogleSheets


class DestinationGoogleSheets(ValmiDestination):
    def __init__(self):
        super().__init__()
        Destination.VALID_CMDS = {"spec", "check", "discover", "write"}

    def write(
        self,
        logger: AirbyteLogger,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredValmiDestinationCatalog,
        input_messages: Iterable[AirbyteMessage],
        # state: Dict[str, any],
    ) -> Iterable[AirbyteMessage]:
        counter = 0

        run_time_args = RunTimeArgs.parse_obj(config["run_time_args"] if "run_time_args" in config else {})
        """
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
                            data={"records_delivered": counter, "finished": False},
                        ),
                    )

                if (datetime.now() - now).seconds > 5:
                    logger.info("A log every 5 seconds - is this required??")

        # Sync completed - final state message
        yield AirbyteMessage(
            type=Type.STATE,
            state=AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                data={"records_delivered": counter, "finished": True},
            ),
        )
        """

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiDestinationCatalog:
        sinks = [ValmiSink(name="GoogleSheets", supported_sync_modes=["upsert"], json_schema={})]
        return ValmiDestinationCatalog(sinks=sinks)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Connection check method for Google Spreadsheets.
        Info:
            Checks whether target spreadsheet_id is available using provided credentials.
        Returns:
            :: Status.SUCCEEDED - if creadentials are valid, token is refreshed, target spreadsheet is available.
            :: Status.FAILED - if could not obtain new token, target spreadsheet is not available or other exception occured (with message).
        """
        spreadsheet_id = get_spreadsheet_id(config["spreadsheet_id"])
        try:
            client = GoogleSheetsClient(config).authorize()
            spreadsheet = GoogleSheets(client, spreadsheet_id)
            check_result = ConnectionTest(spreadsheet).perform_connection_test()
            if check_result:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except RefreshError as token_err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{token_err}")
        except Exception as err:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(err)}")
