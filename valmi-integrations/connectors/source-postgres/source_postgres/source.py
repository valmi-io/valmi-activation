import json
from datetime import datetime
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


class SourcePostgres(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            engine = create_engine(
                "postgresql+psycopg2://{0}:{1}@{2}/{3}".format(
                    config["user"], config["password"], config["host"], config["database"]
                )
            )
            with engine.connect():
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        engine = create_engine(
            "postgresql+psycopg2://{0}:{1}@{2}/{3}".format(
                config["user"], config["password"], config["host"], config["database"]
            )
        )
        with engine.connect() as connection:
            if "streamType" in config and config["streamType"] == "namespace":
                result = connection.execute(text("SELECT schema_name FROM information_schema.schemata;")).fetchall()
                streams = []
                stream_name = "namespaces"
                json_schema = {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {},
                }
                for row in result:
                    json_schema["properties"][row[0]] = {"type": "string"}
                streams.append(
                    AirbyteStream(
                        name=stream_name,
                        json_schema=json_schema,
                        supported_sync_modes=["full_refresh", "incremental"],
                    )
                )
                return AirbyteCatalog(streams=streams)
            else:
                namespace = "public"
                result = connection.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = '{0}';".format(
                            namespace
                        )
                    )
                ).fetchall()

                streams = []
                for row in result:
                    stream_name = row[0]
                    result = connection.execute(
                        text(
                            "SELECT column_name, data_type FROM information_schema.columns \
                                 WHERE table_name = '{0}';".format(
                                stream_name
                            )
                        )
                    ).fetchall()
                    json_schema = {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": {},
                    }
                    for column in result:
                        json_schema["properties"][column[0]] = {"type": "{0}".format(column[1])}
                    streams.append(
                        AirbyteStream(
                            name=stream_name,
                            json_schema=json_schema,
                            supported_sync_modes=["full_refresh", "incremental"],
                        )
                    )
                catalog = AirbyteCatalog(streams=streams)
                catalog.__setattr__("namespace", "public")
                catalog.__setattr__("end", False)
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
