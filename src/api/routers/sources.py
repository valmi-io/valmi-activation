import io
import subprocess

from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic.types import Any, Json

from api.services import OrdersService, get_orders_service

router = APIRouter(prefix="/sources")


@router.get("/spec", response_model=Json[Any])
async def list_orders(
    orders_service: OrdersService = Depends(get_orders_service),
) -> Json[Any]:
    lines = []
    proc = subprocess.Popen(["docker", "run", "--rm", "valmi/source-postgres:dev", "spec"], stdout=subprocess.PIPE)
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        lines.append(line)
    return "\n".join(lines)
