import json
from datetime import datetime
import os
from typing import Any, Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)

from airbyte_cdk.sources import Source
from sqlalchemy import create_engine, text
from .dbt_airbyte_adapter import DbtAirbyteAdpater


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

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        self.initialize(logger, config)

        # TODO: using sequential discover methodology for now.
        logger.debug("Discovering streams...")
        more, result_streams = self.dbt_adapter.discover_streams(logger=logger, config=config)

        if more:
            streams = []
            stream_name = "namespace"
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {},
            }
            for row in result_streams:
                json_schema["properties"][str(row)] = {"type": "string"}

            streams.append(
                AirbyteStream(
                    name=stream_name,
                    json_schema=json_schema,
                    supported_sync_modes=["full_refresh", "incremental"],
                )
            )
            catalog = AirbyteCatalog(streams=streams)
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
                    AirbyteStream(
                        name=stream_name,
                        json_schema=json_schema,
                        supported_sync_modes=["full_refresh", "incremental"],
                    )
                )
            catalog = AirbyteCatalog(streams=streams)
            catalog.__setattr__("type", "table")
            catalog.__setattr__("more", more)
            return catalog

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        engine = create_engine(
            "postgresql+psycopg2://{0}:{1}@{2}/{3}".format(
                config["user"], config["password"], config["host"], config["database"]
            )
        )
        with engine.connect() as connection:
            stream_name = catalog.streams[0].stream.name
            columns = catalog.streams[0].stream.json_schema["properties"].keys()
            result = connection.execute(text("SELECT {1} FROM {0};".format(stream_name, ",".join(columns)))).fetchall()
            for row in result:
                data: Dict[str, Any] = {}
                for i in range(len(row)):
                    data[list(columns)[i]] = row[i]
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000
                    ),
                )
