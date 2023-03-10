from typing import Any, Optional
from pydantic import BaseModel, UUID4, Json
from datetime import datetime
from .utils import to_camel


class SyncRunBase(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SyncRunUpdate(SyncRunBase):
    status: Optional[str]
    metrics: Optional[Json[Any]]
    remarks: Optional[Json[Any]]
    dagster_run_id: Optional[str]


class SyncRunCreate(SyncRunBase):
    sync_id: UUID4
    run_id: UUID4
    run_at: datetime
    status: str
    metrics: Optional[Json[Any]]
    remarks: Optional[Json[Any]]


class SyncRun(SyncRunCreate):
    run_id: UUID4

    class Config:
        orm_mode = True
