from typing import Any

from fastapi import FastAPI
from pydantic import Json


def create_app() -> FastAPI:
    app = FastAPI(
        title="valmi.io",
        description="Rest API for valmi engine",
        version="1.0",
    )

    @app.get("/health")
    async def health() -> Json[Any]:
        return {"message": "Hello World"}

    @app.get("/")
    async def root() -> Json[Any]:
        return {"message": "Hello World"}

    from api.routers import orders, products, stores

    app.include_router(orders.router)
    app.include_router(products.router)
    app.include_router(stores.router)
    return app
