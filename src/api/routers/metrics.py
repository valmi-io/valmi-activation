import logging

from fastapi import Depends

from fastapi.routing import APIRouter
from vyper import v
from api.schemas import MetricCreate, Metric
from api.services import MetricsService, get_metrics_service
from metastore import models

router = APIRouter(prefix="/metrics")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.post(
    "/",
    response_model=Metric,
    status_code=201,
    responses={409: {"description": "Conflict Error"}},
)
async def create_metric(
    metric: MetricCreate, metric_service: MetricsService = Depends(get_metrics_service)
) -> models.Store:
    return metric_service.create(metric)
