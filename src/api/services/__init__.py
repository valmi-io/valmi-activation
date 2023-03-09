from fastapi import Depends
from sqlalchemy.orm import Session

from metastore.session import get_session


from .syncs import SyncsService
from .sync_runs import SyncRunsService
from .metrics import MetricsService


def get_syncs_service(db_session: Session = Depends(get_session)) -> SyncsService:
    return SyncsService(db_session)


def get_sync_runs_service(db_session: Session = Depends(get_session)) -> SyncRunsService:
    return SyncRunsService(db_session)


def get_metrics_service() -> MetricsService:
    return MetricsService()


__all__ = (
    "get_syncs_service",
    "get_sync_runs_service",
    "get_metrics_service",
)
