import json
from typing import Any

from fastapi import FastAPI
from pydantic import Json

from orchestrator.Orchestrator import Orchestrator


def create_app() -> FastAPI:
    orchestrator = Orchestrator()

    app = FastAPI(
        title="valmi.io",
        description="Rest API for valmi engine",
        version="1.0",
    )

    @app.get("/health")
    async def health() -> Json[Any]:
        return json.dumps({"status": "ok"})

    @app.get("/")
    async def root() -> Json[Any]:
        return json.dumps({"message": "Hello World"})

    @app.on_event("shutdown")
    def shutdown_event() -> None:
        orchestrator.destroy()

    from api.routers import orders, products, sources, stores

    app.include_router(orders.router)
    app.include_router(products.router)
    app.include_router(stores.router)
    app.include_router(sources.router)

    return app
