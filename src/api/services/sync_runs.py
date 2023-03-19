from datetime import datetime
from pydantic import UUID4
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from metastore.models import SyncRun
from api.schemas import SyncRunCreate
from typing import Any, List

from metastore.models import SyncStatus
from .base import BaseService


class SyncRunsService(BaseService[SyncRun, SyncRunCreate, Any]):
    def __init__(self, db_session: Session):
        super(SyncRunsService, self).__init__(SyncRun, db_session)

    def create(self, obj: SyncRunCreate) -> SyncRun:
        return super().create(obj)

    def get_runs(self, sync_id: UUID4, before: datetime, limit: int) -> List[SyncRun]:
        return (
            self.db_session.query(self.model)
            .filter(and_(SyncRun.run_at < before), SyncRun.sync_id == sync_id)
            .order_by(SyncRun.run_at.desc())
            .limit(limit)
            .all()
        )

    def get_active_or_latest_runs(self, after: datetime) -> List[SyncRun]:
        return (
            self.db_session.query(self.model)
            .filter(or_(SyncRun.run_at > after, SyncRun.status != SyncStatus.STOPPED.value))
            .all()
        )

    def save_status(self, sync_id, run_id, connector_string, status):
        sync_run = self.get(run_id)
        if not sync_run.extra:
            sync_run.extra = {}
        if connector_string not in sync_run.extra:
            sync_run.extra[connector_string] = {}

        sync_run.extra[connector_string]["status"] = status
        self.db_session.commit()

    def save_state(self, sync_id, run_id, connector_string, state):
        sync_run = self.get(run_id)
        if not sync_run.extra:
            sync_run.extra = {}
        if connector_string not in sync_run.extra:
            sync_run.extra[connector_string] = {}
        sync_run.extra[connector_string]["state"] = {"state": state}
        self.db_session.commit()
