"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Sunday, March 19th 2023, 12:47:57 pm
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

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Extra, Field
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteStream,
    ConfiguredAirbyteStream,
    ConfiguredAirbyteCatalog,
    AirbyteRecordMessage,
)
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
    mirror = "mirror"
    append = "append"
    update = "update"
    create = "create"


class FieldCatalog(BaseModel):
    class Config:
        extra = Extra.allow

    json_schema: Optional[Dict[str, Any]] = Field(..., description="Sink schema using Json Schema specs.")
    supported_destination_ids: Optional[List[str]] = Field(
        ..., description="List of supported_destination ids", min_items=0
    )
    allow_freeform_fields: bool = Field(..., description="Allow freeform fields in destination.")
    template_fields: Optional[Dict[str, Any]] = Field(None, description="Templated fields for destination, rendered using Jinja with mapped fields. Some connectors like Slack and Android push notifications can use this to generate user friendly messages.")
    mandatory_fields: Optional[List[str]] = Field(None, description="List of mandatory fields for destination.")


class ValmiSink(BaseModel):
    class Config:
        extra = Extra.allow

    supported_destination_sync_modes: List[DestinationSyncMode] = Field(
        ..., description="List of sync modes supported by this sink.", min_items=1
    )

    name: str = Field(..., description="Sink's unique name.")
    label: str = Field(..., description="Sink's Display Label.")

    field_catalog: Dict[str, FieldCatalog] = Field(..., description="Sink Fields mapped by Destination Sync Mode")


class ConfiguredValmiSink(BaseModel):
    class Config:
        extra = Extra.allow

    sink: ValmiSink = None
    destination_sync_mode: DestinationSyncMode
    mapping: list[Dict[str, Any]] = Field(..., description="Create mapping from source to destination fields.")
    destination_id: Optional[str]
    template_fields: Optional[Dict[str, str]] = Field(None, description="Configured template fields by the user from the UI.")


# TODO: Hack. Think of a nice way
@optional
class ValmiDestinationCatalog(AirbyteCatalog):
    class Config:
        extra = Extra.allow

    sinks: Optional[List[ValmiSink]]
    allow_object_creation: bool = Field(..., description="Allow object creation in destination.")
    object_schema: Dict[str, Any] = Field(..., description="Object creation schema using Json Schema specs.")
    more: bool = False
    type: str = Field(..., description="Type of the object.")


class ConfiguredValmiDestinationCatalog(BaseModel):
    class Config:
        extra = Extra.allow

    sinks: List[ConfiguredValmiSink]


# TODO: Hack. Think of a nice way
@optional
class ValmiStream(AirbyteStream):
    supported_destination_sync_modes: List[DestinationSyncMode] = Field(
        ..., description="List of destination sync modes supported by this stream.", min_items=1
    )
    label: str = Field(..., description="Stream's Display Label.")
    pass


class ConfiguredValmiStream(ConfiguredAirbyteStream):
    class Config:
        extra = Extra.allow

    stream: ValmiStream
    destination_sync_mode: DestinationSyncMode


# TODO: Hack. Think of a nice way
@optional
class ValmiCatalog(AirbyteCatalog):
    class Config:
        extra = Extra.allow

    streams: Optional[List[ValmiStream]]


class ConfiguredValmiCatalog(ConfiguredAirbyteCatalog):
    class Config:
        extra = Extra.allow

    streams: List[ConfiguredValmiStream]


class ValmiFinalisedRecordMessage(AirbyteRecordMessage):
    rejected: Optional[bool] = Field(default=False, description="Record is rejected.")
    rejection_metadata: Optional[Dict[str, Any]] = Field(description="Metadata for rejection.")
    rejection_message: Optional[str] = Field(description="Message for rejection.")
    rejection_code: Optional[str] = Field(description="Code for rejection.")
    metric_type: str = Field(..., description="Metric type for the record.")
    synthetic_internal_id: Optional[str] = Field(description="Artificial unique record id for the record, \
                                     used for dedup within a sync.")