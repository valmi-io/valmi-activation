from datetime import datetime
from pydantic import UUID4
from sqlalchemy import and_
from sqlalchemy.orm import Session

from metastore.models import SyncRun
from api.schemas import SyncRunCreate
from typing import Any, List
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
