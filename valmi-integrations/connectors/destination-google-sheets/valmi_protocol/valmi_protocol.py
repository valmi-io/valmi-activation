from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Extra, Field
from airbyte_cdk.models import AirbyteCatalog, AirbyteStream
import inspect


def optional(*fields):
    """Decorator function used to modify a pydantic model's fields to all be optional.
    Alternatively, you can  also pass the field names that should be made optional as arguments
    to the decorator.
    Taken from https://github.com/samuelcolvin/pydantic/issues/1223#issuecomment-775363074
    """

    def dec(_cls):
        for field in fields:
            _cls.__fields__[field].required = False
        return _cls

    if fields and inspect.isclass(fields[0]) and issubclass(fields[0], BaseModel):
        cls = fields[0]
        fields = cls.__fields__
        return dec(cls)

    return dec


class DestinationSyncMode(Enum):
    upsert = "upsert"


class ValmiSink(BaseModel):
    class Config:
        extra = Extra.allow

    supported_sync_modes: List[DestinationSyncMode] = Field(
        ..., description="List of sync modes supported by this sink.", min_items=1
    )

    # SINK object -- Hubspot kind of destinations can populate this - Webhooks are empty
    name: str = Field(..., description="Sink's name.")
    json_schema: Optional[Dict[str, Any]] = Field(..., description="Sink schema using Json Schema specs.")


class ConfiguredValmiSink(BaseModel):
    class Config:
        extra = Extra.allow

    sink: ValmiSink = None
    destination_sync_mode: DestinationSyncMode
    mapping: Dict[str, Any] = Field(..., description="Create mapping from source to destination fields.")


# TODO: Hack. Think of a nice way
@optional
class ValmiStream(AirbyteStream):
    pass


# TODO: Hack. Think of a nice way
@optional
class ValmiDestinationCatalog(AirbyteCatalog):
    class Config:
        extra = Extra.allow

    sinks: Optional[List[ValmiSink]]


class ConfiguredValmiDestinationCatalog(BaseModel):
    class Config:
        extra = Extra.allow

    sinks: List[ConfiguredValmiSink]
