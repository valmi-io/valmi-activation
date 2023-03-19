import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey
from enum import Enum


class SyncConfigStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class SyncStatus(str, Enum):
    STOPPED = "stopped"
    FAILED = "failed"
    RUNNING = "running"
    SCHEDULED = "scheduled"


Base: Any = declarative_base()


class SyncSchedule(Base):
    __tablename__ = "sync_schedules"

    sync_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    last_run_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    last_run_id = sa.Column(UUID(as_uuid=True), nullable=True)
    run_interval = sa.Column(sa.Integer, nullable=False)
    status = sa.Column(sa.Text, nullable=False)
    run_status = sa.Column(sa.Text, nullable=False, default=SyncStatus.STOPPED)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)


class SyncRun(Base):
    __tablename__ = "sync_runs"

    sync_id = sa.Column(ForeignKey("sync_schedules.sync_id"), nullable=False)
    run_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    status = sa.Column(sa.Text, nullable=False)
    metrics = sa.Column(sa.JSON, nullable=True)
    extra = sa.Column(sa.JSON, nullable=True)  # store error messages or anything else
    dagster_run_id = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
