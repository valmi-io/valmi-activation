from typing import List

from fastapi import Depends
from fastapi.routing import APIRouter

from api.services import OrdersService, get_orders_service
from db import models
from db.schemas import Order

router = APIRouter(prefix="/sources")


@router.get("/spec", response_model=List[Order])
async def list_orders(
    orders_service: OrdersService = Depends(get_orders_service),
) -> List[models.Order]:
    return orders_service.list()
