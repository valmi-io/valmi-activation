import json
from datetime import datetime
import os
from typing import Any, Dict, Generator
import subprocess
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteErrorTraceMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)

from airbyte_cdk.sources import Source
from valmi_dbt.dbt_airbyte_adapter import DbtAirbyteAdpater, CustomFalDbt
from valmi_protocol.valmi_protocol import ValmiCatalog, ValmiStream


class SourcePostgres(Source):
    def initialize(self, logger: AirbyteLogger, config):
        os.environ["DO_NOT_TRACK"] = "True"
        os.environ["FAL_STATS_ENABLED"] = "False"

        logger.debug("Generating dbt profiles.yml")
        self.dbt_adapter = DbtAirbyteAdpater()
        self.dbt_adapter.write_profiles_config_from_spec(logger, config, "profiles.yml")
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

    def execute_dbt(self, logger: AirbyteLogger):
        logger.info("Initiating dbt run")

        proc = subprocess.Popen("dbt --log-format json run".split(" "), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        while True:
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                logger.info("Waiting for dbt to finish...")
                continue
            break

        logs = proc.stdout.readlines()
        lastError = None
        for log in logs:
            j = json.loads(log.decode())
            if j["info"]["level"].lower() == "error":
                lastError = j

        if proc.returncode is not None and proc.returncode != 0:
            raise Exception(lastError["info"]["msg"])
        else:
            logger.info("Dbt run successful")

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        self.initialize(logger, config)

        # extract sync_id from the run_time_args
        if hasattr(catalog, "run_time_args") and "sync_id" in catalog.run_time_args:
            sync_id = catalog.run_time_args["sync_id"]
        else:
            sync_id = "default_sync_id"

        # finalise the dbt package
        self.dbt_adapter.generate_project_yml(logger, catalog, sync_id, "dbt_project.yml")
        self.dbt_adapter.generate_source_yml(logger, config, catalog, "models/staging/schema.yml")

        try:
            self.execute_dbt(logger=logger)
        except Exception as e:
            yield AirbyteErrorTraceMessage(message=str(e))
            return

        # initialise chunk_size
        if hasattr(catalog, "run_time_args") and "chunk_size" in catalog.run_time_args:
            chunk_size = catalog.run_time_args["chunk_size"]
        else:
            chunk_size = 10

        # now read data from the dbt transit snapshot
        faldbt = CustomFalDbt(
            basic=True, profiles_dir=self.get_cur_dir(), project_dir=self.get_abs_path("valmi_dbt_source_transform")
        )
        while True:
            columns = catalog.streams[0].stream.json_schema["properties"].keys()
            results = self.dbt_adapter.execute_sql(
                faldbt,
                "SELECT {1} FROM {{ ref('transit_snapshot_{0}') }} LIMIT {2};".format(
                    sync_id, ",".join(columns), chunk_size
                ),
            )
            for row in results:
                data: Dict[str, Any] = {}
                for i in range(len(row)):
                    data[list(columns)[i]] = row[i]
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=catalog.streams[0].stream.name,
                        data=data,
                        emitted_at=int(datetime.now().timestamp()) * 1000,
                    ),
                )
            if len(results) <= 0:
                return
