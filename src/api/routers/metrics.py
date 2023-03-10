import logging
from typing import Any

from fastapi import Depends

from fastapi.routing import APIRouter
from pydantic import UUID4
from vyper import v
from api.schemas import MetricCreate, MetricBase, GenericResponse
from api.services import MetricsService, get_metrics_service

router = APIRouter(prefix="/metrics")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.post(
    "/",
    response_model=GenericResponse,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
)
async def create_metric(
    metric: MetricCreate, metric_service: MetricsService = Depends(get_metrics_service)
) -> GenericResponse:
    metric_service.create(metric)
    return GenericResponse()


@router.get("/syncs/{sync_id}/runs/{run_id}", response_model=dict[str, Any])
async def get_metrics(
    sync_id: UUID4, run_id: UUID4, metric_service: MetricsService = Depends(get_metrics_service)
) -> dict[str, Any]:
    x = metric_service.get_metrics(MetricBase(run_id=run_id, sync_id=sync_id))
    print(x)
    return x
