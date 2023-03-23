import logging
from typing import Any

from fastapi import Depends

from fastapi.routing import APIRouter
from pydantic import UUID4

"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, March 9th 2023, 8:09:28 pm
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


@router.get("/syncs/{sync_id}/runs/{run_id/metrics", response_model=dict[str, Any])
async def get_metrics(
    sync_id: UUID4, run_id: UUID4, metric_service: MetricsService = Depends(get_metrics_service)
) -> dict[str, Any]:
    x = metric_service.get_metrics(MetricBase(run_id=run_id, sync_id=sync_id))
    # print(x)
    return x
