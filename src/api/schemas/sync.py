from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from .utils import to_camel


class SyncScheduleBase(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class SyncScheduleCreate(SyncScheduleBase):
    sync_id: UUID4
    last_run_at: Optional[datetime]
    run_interval: Optional[int]
    status: Optional[str]


class SyncSchedule(SyncScheduleCreate):
    run_status: Optional[str]

    class Config:
        orm_mode = True


class SyncCurrentRunArgs(BaseModel):
    run_id: UUID4
    sync_id: UUID4
    chunk_size: int
    chunk_id: int
    records_per_metric: int

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
