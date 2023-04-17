"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, March 22nd 2023, 2:17:33 pm
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
from datetime import datetime
import os
from typing import Any, Dict, Generator, Sequence
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteErrorTraceMessage,
    AirbyteTraceMessage,
    AirbyteStateMessage,
    AirbyteEstimateTraceMessage,
    Status,
    Type,
    EstimateType,
    AirbyteStateType,
    TraceType,
    SyncMode,
)

from airbyte_cdk.sources import Source
from valmi_dbt.dbt_airbyte_adapter import DbtAirbyteAdpater
from valmi_lib.valmi_protocol import add_event_meta
from valmi_lib.valmi_protocol import ValmiCatalog, ValmiStream, ConfiguredValmiCatalog, DestinationSyncMode
from fal import FalDbt
from dbt.contracts.results import RunResultOutput, RunStatus


class SourcePostgres(Source):
    def initialize(self, logger: AirbyteLogger, config):
        os.environ["DO_NOT_TRACK"] = "True"
        os.environ["FAL_STATS_ENABLED"] = "False"

        logger.debug("Generating dbt profiles.yml")
        self.dbt_adapter = DbtAirbyteAdpater()
        self.dbt_adapter.write_profiles_config_from_spec(logger, config)
        logger.debug("dbt profiles.yml generated")

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        self.initialize(logger, config)

        try:
            self.dbt_adapter.check_connection()
            logger.debug("connection success")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.debug("connection failed")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> ValmiCatalog:
        self.initialize(logger, config)

        # TODO: using sequential discover methodology for now.
        logger.debug("Discovering streams...")
        more, result_streams = self.dbt_adapter.discover_streams(logger=logger, config=config)

        if more:
            streams = []

            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            }
            for row in result_streams:
                streams.append(
                    ValmiStream(
                        name=str(row),
                        supported_destinaton_sync_modes=(DestinationSyncMode.upsert, DestinationSyncMode.mirror),
                        supported_sync_modes=(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                        # json_schema=json_schema,
                    )
                )
            catalog = ValmiCatalog(streams=streams)
            catalog.__setattr__("type", "namespace")
            catalog.__setattr__("more", more)
            return catalog
        else:
            streams = []
            for row in result_streams:
                stream_name = str(row)

                json_schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {},
                }
                for column in self.dbt_adapter.get_columns(self.dbt_adapter.adapter, row):
                    json_schema["properties"][str(column)] = {"type": "{0}".format(str(column))}

                streams.append(
                    ValmiStream(
                        name=stream_name,
                        supported_sync_modes=["full_refresh", "incremental"],
                        json_schema=json_schema,
                    )
                )
            catalog = ValmiCatalog(streams=streams)
            catalog.__setattr__("type", "table")
            catalog.__setattr__("more", more)
            return catalog

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredValmiCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        self.initialize(logger, config)

        # extract sync_id from the run_time_args
        if "run_time_args" in config and "sync_id" in config["run_time_args"]:
            sync_id = config["run_time_args"]["sync_id"]
        else:
            sync_id = "default_sync_id"

        # finalise the dbt package
        self.dbt_adapter.generate_project_yml(logger, config, catalog, sync_id)
        self.dbt_adapter.generate_source_yml(logger, config, catalog, sync_id)
        self.dbt_adapter.append_sql_files_with_sync_id(sync_id)

        try:
            self.dbt_adapter.execute_dbt(logger=logger)
        except Exception as e:
            error_msg = str(e)
            faldbt: FalDbt = self.dbt_adapter.get_fal_dbt(_basic=False)
            # Accessing hidden variable _run_results
            if faldbt._run_results is not None:
                results: Sequence[RunResultOutput] = faldbt._run_results.results
                for result in results:
                    if result.status == RunStatus.Error:
                        error_msg = result.message
                        break
            yield AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    error=AirbyteErrorTraceMessage(message=error_msg),
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            return

        # initialise chunk_size
        if "run_time_args" in config and "chunk_size" in config["run_time_args"]:
            chunk_size = config["run_time_args"]["chunk_size"]
        else:
            chunk_size = 300

        # now read data from the dbt transit snapshot
        faldbt = self.dbt_adapter.get_fal_dbt()

        # release metrics
        for metric_msg in self.generate_sync_metrics(faldbt, logger=logger, sync_id=sync_id, catalog=catalog):
            yield metric_msg

        if catalog.streams[0].destination_sync_mode == DestinationSyncMode.upsert:
            tables_to_sync = [
                {
                    "table": f"ref('transit_snapshot_{sync_id}')",
                    "columns": catalog.streams[0].stream.json_schema["properties"].keys(),
                }
            ]
        elif catalog.streams[0].destination_sync_mode == DestinationSyncMode.mirror:
            tables_to_sync = [
                # TODO: becoming spahgetti code. Need to refactor
                {"table": "source('scratch', var('cleanup_snapshot'))", "columns": [catalog.streams[0].id_key]},
                {
                    "table": f"ref('transit_snapshot_{sync_id}')",
                    "columns": catalog.streams[0].stream.json_schema["properties"].keys(),
                },
            ]

        # set the below two values from the checkpoint state
        chunk_id = 0
        for loop_var, item in enumerate(tables_to_sync):
            last_row_num = -1
            while True:
                columns = item["columns"]
                adapter_resp, agate_table = self.dbt_adapter.execute_sql(
                    faldbt,
                    "SELECT _valmi_row_num, _valmi_sync_op, {1} \
                        FROM {{{{ {0} }}}} \
                        WHERE _valmi_row_num > {3} \
                        LIMIT {2};".format(
                        item["table"], ",".join(columns), chunk_size, last_row_num
                    ),
                )

                for row in agate_table.rows:
                    data: Dict[str, Any] = {}
                    for i in range(len(row)):
                        if agate_table.column_names[i].startswith("_valmi"):
                            add_event_meta(data, agate_table.column_names[i], row[i])
                        else:
                            data[agate_table.column_names[i]] = row[i]
                    last_row_num = row[0]

                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(
                            stream=catalog.streams[0].stream.name,
                            data=data,
                            emitted_at=int(datetime.now().timestamp()) * 1000,
                        ),
                    )
                if len(agate_table.rows) <= 0:
                    break
                else:
                    chunk_id += 1
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=AirbyteStateMessage(type=AirbyteStateType.STREAM, data={"chunk_id": chunk_id}),
                        emitted_at=int(datetime.now().timestamp()) * 1000,
                    )
            if loop_var == len(tables_to_sync) - 1:
                return

    def read_catalog(self, catalog_path: str) -> ConfiguredValmiCatalog:
        return ConfiguredValmiCatalog.parse_obj(self._read_json_file(catalog_path))

    def generate_sync_metrics(self, faldbt, logger, sync_id, catalog) -> Generator[AirbyteMessage, None, None]:
        adapter_resp, agate_table = self.dbt_adapter.execute_sql(
            faldbt,
            "SELECT * FROM {{{{ ref('sync_metrics_{0}') }}}}".format(sync_id),
        )

        for row in agate_table.rows.values():
            yield AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ESTIMATE,
                    estimate=AirbyteEstimateTraceMessage(
                        name=catalog.streams[0].stream.name,
                        type=EstimateType.STREAM,
                        row_estimate=row["count"],
                        row_kind=f'{row["kind"]}$${row["error_code"]}',
                    ),
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
