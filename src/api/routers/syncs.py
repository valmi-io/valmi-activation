from datetime import datetime
import logging
from typing import Any, List

from fastapi import Depends

from fastapi.routing import APIRouter
from pydantic import UUID4, Json
from vyper import v

from metastore import models
from api.schemas import SyncSchedule, SyncRun
from api.services import SyncsService, get_syncs_service, SyncRunsService, get_sync_runs_service

router = APIRouter(prefix="/syncs")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.get("/", response_model=List[SyncSchedule])
async def get_sync_schedules(
    sync_service: SyncsService = Depends(get_syncs_service),
) -> List[models.SyncSchedule]:
    return sync_service.list()


@router.get("/{sync_id}/runs/", response_model=List[SyncRun])
async def get_sync_runs(
    before: datetime = None,
    limit: int = 0,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> List[models.SyncRun]:
    ## MAJOR ITEM
    pass
    # return sync_runs_service.list()


@router.get("/sync/{sync_id}/run/{run_id}/samples/{connector_id}", response_model=Json[Any])
async def get_run_samples(
    sync_id: UUID4,
    run_id: UUID4,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> Json[Any]:
    ## MAJOR ITEM
    pass
    # return sync_runs_service.list()
