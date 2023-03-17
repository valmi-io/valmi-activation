from typing import Dict, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime


class SyncRunBase(BaseModel):
    class Config:
        allow_population_by_field_name = True


class SyncRunUpdate(SyncRunBase):
    status: Optional[str]
    metrics: Optional[Dict]
    remarks: Optional[Dict]
    dagster_run_id: Optional[str]


class SyncRunCreate(SyncRunBase):
    sync_id: UUID4
    run_id: UUID4
    run_at: datetime
    status: str
    metrics: Optional[Dict]
    remarks: Optional[Dict]


class SyncRun(SyncRunCreate):
    run_id: UUID4

    class Config:
        orm_mode = True
