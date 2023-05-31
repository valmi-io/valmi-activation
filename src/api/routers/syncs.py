"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Tuesday, March 21st 2023, 6:56:16 pm
Author: Rajashekar Varkala @ valmi.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import copy
import logging
import uuid

from datetime import datetime
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
from api.schemas.sync_run import ConnectorSynchronization, SyncRunTimeArgs
from metastore.models import SyncStatus, SyncConfigStatus
from api.schemas import SyncRunCreate
from metrics import MetricDisplayOrder


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
    if previous_run is not None:
        sync_runs_service.db_session.refresh(
            previous_run
        )  # TODO: Have to find a better way instead of so many refreshes

    # TODO: get saved checkpoint state of the run_id & create column run_time_args in the sync_runs table to get repeatable runs
    run_args = {
        "sync_id": sync_id,
        "run_id": sync_schedule.last_run_id,
        "chunk_size": 300,
        "chunk_id": 0,
        "records_per_metric": 10,
        "previous_run_status": "success" if previous_run is None
        or ("run_manager" in previous_run.extra and previous_run.extra["run_manager"]["status"]["status"] == "success")
        else "failure",  # For first run also, previous_run_status will be success
    }

    # Get run time args from run object
    current_run = runs[0]
    if current_run.run_time_args is not None and "full_refresh" in current_run.run_time_args:
        run_args["full_refresh"] = current_run.run_time_args["full_refresh"]

    return SyncCurrentRunArgs(**run_args)


@router.get("/{sync_id}/runs/{run_id}/synchronize_connector_engine", response_model=ConnectorSynchronization)
async def synchronize_connector(
    sync_id: UUID4,
    run_id: UUID4,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> ConnectorSynchronization:
    run = sync_runs_service.get(run_id)
    abort_required = False

    print(f"Run tagas extra: {run.extra}")
    if run.extra is not None:
        for key in ["src", "dest"]:
            key_value = run.extra.get(key, {})
            status = key_value.get("status", {}).get("status", "")
            if status == "failed":
                abort_required = True
                break

        run_state = run.extra.get("run_manager", {}).get("status", {})
        if run_state.get("status", "") == "terminated":
            abort_required = True

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


@router.post("/{sync_id}/runs/{run_id}/abort", response_model=GenericResponse)
async def abort(
    sync_id: UUID4,
    run_id: UUID4,
    sync_service: SyncsService = Depends(get_syncs_service),
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
) -> GenericResponse:

    sync = sync_service.get_sync(sync_id)
    run = sync_runs_service.get(run_id)

    if run.status == SyncStatus.RUNNING: 
        # Set connector run_manager status to terminated to stop source and destination connections
        run_status = {
            "status": "terminated",
            "message": "Run aborted by user",
        }
        sync_runs_service.update_sync_run_extra_data(run_id, "run_manager", "status", run_status)

        # Update sync and run status to "ABORTING" so that
        # current running sync will get aborted by run manager
        sync.run_status = SyncStatus.ABORTING
        run.status = SyncStatus.ABORTING
        sync_service.update_sync_and_run(sync, run)

    else:
        return GenericResponse(success=False, message=f"Connot stop sync run with status '{run.status}'")

    return GenericResponse(success=True, message="success")


@router.post("/{sync_id}/runs/create", response_model=GenericResponse)
async def new_run(
    sync_id: UUID4,
    run_time_args: SyncRunTimeArgs,
    sync_service: SyncsService = Depends(get_syncs_service),
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
):
    sync = sync_service.get_sync(sync_id)
    runs = sync_runs_service.get_runs(sync_id, datetime.now(), 2)
    previous_run = runs[1] if len(runs) > 1 else None
    previous_run_status = previous_run.status if previous_run is not None else None

    if sync.status == SyncConfigStatus.ACTIVE and (
        previous_run is None or previous_run.status == SyncStatus.STOPPED
    ):
        sync.run_status = SyncStatus.ABORTING

        run = SyncRunCreate(
            run_id=uuid.uuid4(),
            sync_id=sync.sync_id,
            run_at=datetime.now(),
            status=SyncStatus.SCHEDULED,
            run_time_args=run_time_args.run_time_args
        )

        sync.last_run_at = run.run_at
        sync.run_status = SyncStatus.SCHEDULED
        sync.last_run_id = run.run_id

        sync_service.update_sync_and_create_run(sync, run)

        return GenericResponse(success=True, message=f"Sync run started with run_id: {run.run_id}")
    else:
        return GenericResponse(
            success=False, 
            message=f"Cannot start the sync run with status: {sync.status}, "
            f"with previous run status: {previous_run_status}"
        )


@router.get("/{sync_id}/runs/", response_model=List[SyncRun])
async def get_sync_runs(
    sync_id: UUID4,
    before: datetime = datetime.now(),
    limit: int = 25,
    sync_runs_service: SyncRunsService = Depends(get_sync_runs_service),
    metric_service: MetricsService = Depends(get_metrics_service),
) -> List[models.SyncRun]:
    runs = sync_runs_service.get_runs(sync_id=sync_id, before=before, limit=limit)
    metrics_display_order = MetricDisplayOrder()

    runs_copy = []
    for run in runs:
        if run.status == "running":
            sync_runs_service.db_session.refresh(run)
            assign_metrics_to_run(run, metric_service)

        run_copy = copy.deepcopy(run)
        if run_copy.metrics:
            run_copy.metrics = metrics_display_order.format(run_copy.metrics)
        
        runs_copy.append(run_copy)
    return runs_copy


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
    sync_runs_service.db_session.refresh(sync_run)

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
