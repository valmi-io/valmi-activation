"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

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
from valmi_connector_lib.valmi_protocol import add_event_meta
from valmi_connector_lib.valmi_protocol import ValmiFinalisedRecordMessage, ValmiCatalog, \
    ValmiStream, ConfiguredValmiCatalog, DestinationSyncMode
from fal import FalDbt
from dbt.contracts.results import RunResultOutput, RunStatus


class SourceSnowflake(Source):
    def initialize(self, logger: AirbyteLogger, config):
        os.environ["DO_NOT_TRACK"] = "True"
        os.environ["FAL_STATS_ENABLED"] = "False"

        logger.debug("Generating dbt profiles.yml")
        self.dbt_adapter = DbtAirbyteAdpater()
        self.dbt_adapter.write_profiles_config_from_spec(logger, config)
        logger.debug("dbt profiles.yml generated")

        logger.debug("Generatign dummy dbt_project file")
        self.dbt_adapter.generate_dummy_project_yml(logger)

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
        more, result_streams, type = self.dbt_adapter.discover_streams(logger=logger, config=config)

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
                        label=str(row),

                        supported_destination_sync_modes=(DestinationSyncMode.upsert, DestinationSyncMode.mirror),
                        supported_sync_modes=(SyncMode.full_refresh, SyncMode.incremental)
                        # json_schema=json_schema,
                    )
                )
            catalog = ValmiCatalog(streams=streams)
            catalog.__setattr__("type", type)
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
                    json_schema["properties"][column.column] = {"type": "{0}".format(column.dtype)}

                streams.append(
                    ValmiStream(
                        name=stream_name,
                        label=stream_name,
                        supported_destination_sync_modes=(DestinationSyncMode.upsert, DestinationSyncMode.mirror),
                        supported_sync_modes=(SyncMode.full_refresh, SyncMode.incremental),
                        json_schema=json_schema,
                    )
                )
            catalog = ValmiCatalog(streams=streams)
            catalog.__setattr__("type", type)
            catalog.__setattr__("more", more)
            return catalog

    def is_dbt_run_finished(self, state: Dict[str, any]):
        if state is None or 'state' not in state:
            return False
        return True
    
    def read_chunk_id_checkpoint(self, state: Dict[str, any]):
        if state is not None \
                and 'state' in state \
                and 'data' in state['state'] \
                and 'chunk_id' in state['state']['data']:
            return state['state']['data']['chunk_id'] + 1
        return 1

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

        if not self.is_dbt_run_finished(state):
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

        # release metrics :: if state is present, metrics were already released in the previous instance
        if not self.is_dbt_run_finished(state):
            for metric_msg in self.generate_sync_metrics(faldbt, logger=logger, sync_id=sync_id, catalog=catalog):
                yield metric_msg

        # set the below two values from the checkpoint state
        chunk_id = 0
        last_row_num = -1
        while True:
            columns = catalog.streams[0].stream.json_schema["properties"].keys()
            adapter_resp, agate_table = self.dbt_adapter.execute_sql(
                faldbt,
                "SELECT _valmi_row_num, _valmi_sync_op, {1} \
                    FROM  {{{{ ref('transit_snapshot_{0}') }}}} \
                    WHERE _valmi_row_num > {3} \
                    ORDER BY _valmi_row_num ASC \
                    LIMIT {2};".format(
                    self.dbt_adapter.sanitise_uuid(sync_id), ",".join([f'"{col}"' for col in columns]), chunk_size, last_row_num
                ),
            )

            for row in agate_table.rows:
                data: Dict[str, Any] = {}
                for i in range(len(row)):
                    if agate_table.column_names[i].lower().startswith("_valmi"):
                        add_event_meta(data, agate_table.column_names[i].lower(), row[i])
                    else:
                        data[agate_table.column_names[i]] = row[i]
                last_row_num = row[0]

                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=ValmiFinalisedRecordMessage(
                        stream=catalog.streams[0].stream.name,
                        data=data,
                        emitted_at=int(datetime.now().timestamp()) * 1000,
                        metric_type="success",
                        rejected=False
                    ),
                )
            if len(agate_table.rows) <= 0:
                return
            else:
                yield AirbyteMessage(
                    type=Type.STATE,
                    state=AirbyteStateMessage(type=AirbyteStateType.STREAM, data={"chunk_id": chunk_id}),
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                )
                chunk_id += 1

    def read_catalog(self, catalog_path: str) -> ConfiguredValmiCatalog:
        return ConfiguredValmiCatalog.parse_obj(self._read_json_file(catalog_path))

    def generate_sync_metrics(self, faldbt, logger, sync_id, catalog) -> Generator[AirbyteMessage, None, None]:
        adapter_resp, agate_table = self.dbt_adapter.execute_sql(
            faldbt,
            "SELECT * FROM {{{{ ref('sync_metrics_{0}') }}}}".format(self.dbt_adapter.sanitise_uuid(sync_id)),
        )

        for row in agate_table.rows.values():
            yield AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ESTIMATE,
                    estimate=AirbyteEstimateTraceMessage(
                        name=catalog.streams[0].stream.name,
                        type=EstimateType.STREAM,
                        row_estimate=row["COUNT(*)"],
                        row_kind=f'{row["KIND"]}$${row["ERROR_CODE"]}',
                    ),
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
