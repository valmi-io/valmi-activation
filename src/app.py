"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, March 8th 2023, 11:38:42 am
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

import json
from typing import Any

from fastapi import FastAPI
from pydantic import Json

from vyper import v
import logging
from contextlib import asynccontextmanager
from utils.request_logger import RouterLoggingMiddleware
from observability import setup_observability
from alerts import AlertGenerator

@asynccontextmanager
async def lifespan(app: FastAPI):

    from orchestrator.repo import Repo
    from docker import ImageWarmupManager, ContainerCleaner
    from datastore.datastore_cleaner import DatastoreCleaner
    from api.services import get_metrics_service
    from api.services import get_log_handling_service

    img_manager = ImageWarmupManager()
    container_cleaner = ContainerCleaner()
    datastore_cleaner = DatastoreCleaner()
    repo = Repo()
    log_handling_service = get_log_handling_service()
    
    yield

    logging.info("Shutting down Log Handling Service")
    log_handling_service.exit_log_serving_process()

    logging.info("Shutting down Metrics service")
    get_metrics_service().shutdown()

    logging.info("Shutting down Repo manager")
    repo.destroy()

    logging.info("Shutting down DataStore Cleaner")
    datastore_cleaner.destroy()

    logging.info("Shutting down Container Cleaner")
    container_cleaner.destroy()

    logging.info("Shutting down Image manager")
    img_manager.destroy()

    logging.info("Shutting down Alert Generator")
    AlertGenerator().destroy()

    logging.info("All services shut down successfully")


def create_app() -> FastAPI:
    app = FastAPI(title="valmi.io", description="Rest API for valmi engine", version="1.0", lifespan=lifespan)
    setup_observability(app)

    if v.get_bool("DEBUG"):

        '''
        app.add_middleware(
            RouterLoggingMiddleware,
            logger=logging.getLogger(v.get("LOGGER_NAME"))
        )
        '''
        
        '''
        @app.middleware("http")
        async def log_request(request, call_next):
            response = await call_next(request)
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            logging.info(f"Status code: {response.status_code} {request.} Body { body}")
            # do something with body ...
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        '''

    @app.get("/health")
    async def health() -> Json[Any]:
        return json.dumps({"status": "ok"})

    @app.get("/")
    async def root() -> Json[Any]:
        return json.dumps({"message": "Valmi.io Activation Platform"})

    from api.routers import connectors, syncs, metrics

    app.include_router(connectors.router)
    app.include_router(syncs.router)
    app.include_router(metrics.router)
    return app
