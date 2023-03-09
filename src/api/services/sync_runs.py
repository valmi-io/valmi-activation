from sqlalchemy.orm import Session

from metastore.models import SyncRun
from api.schemas import SyncRunCreate
from typing import Any
from .base import BaseService


class SyncRunsService(BaseService[SyncRun, SyncRun, Any]):
    def __init__(self, db_session: Session):
        super(SyncRunsService, self).__init__(SyncRun, db_session)

    def create(self, obj: SyncRunCreate) -> SyncRun:
        return super().create(obj)
