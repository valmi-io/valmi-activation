from datetime import datetime
import logging
from typing import Any, Dict, List

from fastapi import Depends

from fastapi.routing import APIRouter
from pydantic import UUID4, Json
from vyper import v

from metastore import models
from api.schemas import SyncSchedule, SyncRun, SyncCurrentRunArgs, GenericResponse
from api.services import (
    SyncsService,
    MetricsService,
    get_metrics_service,
    get_syncs_service,
    SyncRunsService,
    get_sync_runs_service,
)
from api.schemas.utils import assign_metrics_to_run
from sqlalchemy.orm.attributes import flag_modified

from api.schemas.metric import MetricBase
from api.schemas.sync_run import ConnectorSynchronization


router = APIRouter(prefix="/syncs")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.get("/", response_model=List[SyncSchedule])
async def get_sync_schedules(
    sync_service: SyncsService = Depends(get_syncs_service),
) -> List[models.SyncSchedule]:
    return sync_service.list()


@router.get("/{sync_id}/runs/current_run_details", response_model=SyncCurrentRunArgs)
async def get_current_run_details(
    sync_id: UUID4,
    sync_service: SyncsService = Depends(get_syncs_service),
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> SyncCurrentRunArgs:
    sync_schedule = sync_service.get(sync_id)
    runs = sync_runs_service.get_runs(sync_id, datetime.now(), 2)
    previous_run = runs[1] if len(runs) > 1 else None

    # TODO: get saved checkpoint state of the run_id & create column run_time_args in the sync_runs table to get repeatable runs
    return SyncCurrentRunArgs(
        sync_id=sync_id,
        run_id=sync_schedule.last_run_id,
        chunk_size=300,
        chunk_id=0,
        records_per_metric=10,
        previous_run_status="success"
        if previous_run is None or previous_run.extra["run_manager"]["status"] == "success"
        else "failure",  # For first run also, previous_run_status will be success
    )


@router.get("/{sync_id}/runs/{run_id}/synchronize_connector_engine", response_model=ConnectorSynchronization)
async def synchronize_connector(
    sync_id: UUID4,
    run_id: UUID4,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> ConnectorSynchronization:
    run = sync_runs_service.get(run_id)
    abort_required = False
    keys_to_check = ["src", "dest"]
    for key in keys_to_check:
        if run.extra is not None and key in run.extra.keys() and "status" in run.extra[key].keys():
            if run.extra[key]["status"]["status"] == "failed":
                abort_required = True
                break
    return ConnectorSynchronization(abort_required=abort_required)


@router.post("/{sync_id}/runs/{run_id}/state/{connector_string}/", response_model=GenericResponse)
async def state(
    sync_id: UUID4,
    run_id: UUID4,
    connector_string: str,
    state: Dict,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> GenericResponse:
    sync_runs_service.save_state(sync_id, run_id, connector_string, state)
    return GenericResponse()


@router.post("/{sync_id}/runs/{run_id}/status/{connector_string}/", response_model=GenericResponse)
async def status(
    sync_id: UUID4,
    run_id: UUID4,
    connector_string: str,
    status: Dict,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> GenericResponse:
    sync_runs_service.save_status(sync_id, run_id, connector_string, status)
    return GenericResponse()


@router.get("/{sync_id}/runs/", response_model=List[SyncRun])
async def get_sync_runs(
    sync_id: UUID4,
    before: datetime = datetime.now(),
    limit: int = 25,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
    metric_service: MetricsService = Depends(get_metrics_service),
) -> List[models.SyncRun]:
    runs = sync_runs_service.get_runs(sync_id=sync_id, before=before, limit=limit)
    for run in runs:
        if run.status == "running":
            assign_metrics_to_run(run, metric_service)
    return runs


@router.get("/{sync_id}/runs/finalise_last_run", response_model=GenericResponse)
async def finalise_last_run(
    sync_id: UUID4,
    metric_service: MetricsService = Depends(get_metrics_service),
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
    sync_service: SyncsService = Depends(get_syncs_service),
) -> GenericResponse:
    sync_schedule = sync_service.get(sync_id)

    # get metrics from Metric service
    sync_schedule = sync_service.get(sync_id)
    metrics = metric_service.get_metrics(MetricBase(run_id=sync_schedule.last_run_id, sync_id=sync_id))
    if metrics:
        sync_run = sync_runs_service.get(sync_schedule.last_run_id)
        sync_runs_service.db_session.refresh(sync_run)
        sync_run.metrics = metrics
        flag_modified(sync_run, "metrics")
        sync_runs_service.commit()
        metric_service.clear_metrics(MetricBase(run_id=sync_id, sync_id=sync_run.run_id))

    return GenericResponse(success=True, message="success")


@router.get("/{sync_id}/runs/{run_id}", response_model=SyncRun)
async def get_run(
    sync_id: UUID4,
    run_id: UUID4,
    metric_service: MetricsService = Depends(get_metrics_service),
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> models.SyncRun:
    sync_run = sync_runs_service.get(run_id)
    return assign_metrics_to_run(sync_run, metric_service)


@router.get("/{sync_id}/runs/{run_id}/samples/{connector_id}", response_model=Json[Any])
async def get_run_samples(
    sync_id: UUID4,
    run_id: UUID4,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> Json[Any]:
    ## MAJOR ITEM
    pass
    # return sync_runs_service.list()
