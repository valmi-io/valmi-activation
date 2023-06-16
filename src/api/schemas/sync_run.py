from typing import Dict, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime


class SyncRunBase(BaseModel):
    class Config:
        allow_population_by_field_name = True


class SyncRunUpdate(SyncRunBase):
    status: Optional[str]
    metrics: Optional[Dict]
    extra: Optional[Dict]
    dagster_run_id: Optional[str]


class SyncRunCreate(SyncRunBase):
    sync_id: UUID4
    run_id: UUID4
    run_at: datetime
    status: str
    metrics: Optional[Dict]
    extra: Optional[Dict]
    run_time_args: Optional[Dict]


class SyncRun(SyncRunCreate):
    run_id: UUID4
    run_end_at: datetime

    class Config:
        orm_mode = True


class ConnectorSynchronization(BaseModel):
    abort_required: bool


class SyncRunTimeArgs(BaseModel):
    run_time_args: Dict

