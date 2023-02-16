import json

from airbyte_cdk.models import AirbyteCatalog, AirbyteStream


def get_catalog() -> AirbyteCatalog:
    streams = json.loads(
        """[
                {
                    "name": "actor",
                    "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "actor_id": {
                        "type": "integer"
                        },
                        "last_update": {
                        "type": "timestamp without time zone"
                        },
                        "first_name": {
                        "type": "character varying"
                        },
                        "last_name": {
                        "type": "character varying"
                        }
                    }
                    },
                    "supported_sync_modes": [
                        "full_refresh",
                        "incremental"
                    ]
                },
                {
                    "name": "actor_info",
                    "json_schema": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "actor_id": {
                        "type": "integer"
                        },
                        "first_name": {
                        "type": "character varying"
                        },
                        "last_name": {
                        "type": "character varying"
                        },
                        "film_info": {
                        "type": "text"
                        }
                    }
                    },
                    "supported_sync_modes": [
                        "full_refresh",
                        "incremental"
                    ]
                }]""",
    )

    airbyte_streams = []
    for stream in streams:
        airbyte_streams.append(
            AirbyteStream(
                name=stream["name"],
                json_schema=stream["json_schema"],
                supported_sync_modes=stream["supported_sync_modes"],
            )
        )
    # print(streams)
    return AirbyteCatalog(streams=airbyte_streams)
