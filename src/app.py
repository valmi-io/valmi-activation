import json
from typing import Any

from fastapi import FastAPI, Response
from pydantic import Json

from vyper import v
import logging
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    from orchestrator.repo import Repo
    from docker import ImageWarmupManager, ContainerCleaner

    img_manager = ImageWarmupManager()
    container_cleaner = ContainerCleaner()
    repo = Repo()

    yield

    repo.destroy()
    img_manager.destroy()
    container_cleaner.destroy()


def create_app() -> FastAPI:
    app = FastAPI(title="valmi.io", description="Rest API for valmi engine", version="1.0", lifespan=lifespan)

    if v.get_bool("DEBUG"):

        @app.middleware("http")
        async def log_request(request, call_next):
            response = await call_next(request)
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            logging.info(f"Status code: {response.status_code} Body { body}")
            # do something with body ...
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

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
