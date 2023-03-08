import json
from typing import Any

from fastapi import FastAPI, Response, Request
from pydantic import Json

from orchestrator.repo import Repo
from vyperconfig import v
import logging


def create_app() -> FastAPI:
    repo = Repo()

    app = FastAPI(
        title="valmi.io",
        description="Rest API for valmi engine",
        version="1.0",
    )

    if v.get_bool("DEBUG"):

        class LogRequestsMiddleware:
            def __init__(self, app) -> None:
                self.app = app

            async def __call__(self, scope, receive, send) -> None:
                receive_cached_ = await receive()

                async def receive_cached():
                    return receive_cached_

                request = Request(scope, receive=receive_cached)
                logging.info(f"{request.method} {request.url} {receive_cached_}")
                await self.app(scope, receive_cached, send)

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

        app.add_middleware(LogRequestsMiddleware)

    @app.get("/health")
    async def health() -> Json[Any]:
        return json.dumps({"status": "ok"})

    @app.get("/")
    async def root() -> Json[Any]:
        return json.dumps({"message": "Hello World"})

    @app.on_event("shutdown")
    def shutdown_event() -> None:
        repo.destroy()

    from api.routers import orders, products, sources, stores

    app.include_router(orders.router)
    app.include_router(products.router)
    app.include_router(stores.router)
    app.include_router(sources.router)

    return app
