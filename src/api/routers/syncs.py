from datetime import datetime
import logging
from typing import Any, List

from fastapi import Depends

from fastapi.routing import APIRouter
from pydantic import UUID4, Json
from vyper import v

from metastore import models
from api.schemas import SyncSchedule, SyncRun, SyncCurrentRunArgs
from api.services import SyncsService, get_syncs_service, SyncRunsService, get_sync_runs_service

router = APIRouter(prefix="/syncs")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.get("/", response_model=List[SyncSchedule])
async def get_sync_schedules(
    sync_service: SyncsService = Depends(get_syncs_service),
) -> List[models.SyncSchedule]:
    return sync_service.list()


@router.get("/{sync_id}/runs/current_run_details", response_model=SyncCurrentRunArgs)
async def get_current_run_id(
    sync_id: UUID4,
    sync_service: SyncsService = Depends(get_syncs_service),
) -> SyncCurrentRunArgs:
    sync_schedule = sync_service.get(sync_id)
    # TODO: get saved state of the run_id
    SyncCurrentRunArgs(
        sync_id=sync_id, run_id=sync_schedule.last_run_id, chunk_size=300, chunk_id=0, records_per_metric=10
    )


@router.get("/{sync_id}/runs/", response_model=List[SyncRun])
async def get_sync_runs(
    sync_id: UUID4,
    before: datetime = datetime.now(),
    limit: int = 25,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> List[models.SyncRun]:
    return sync_runs_service.get_runs(sync_id=sync_id, before=before, limit=limit)


@router.get("/{sync_id}/runs/{run_id}/samples/{connector_id}", response_model=Json[Any])
async def get_run_samples(
    sync_id: UUID4,
    run_id: UUID4,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> Json[Any]:
    ## MAJOR ITEM
    pass
    # return sync_runs_service.list()
