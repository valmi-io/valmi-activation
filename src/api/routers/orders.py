from typing import List, Optional

from fastapi import Depends
from fastapi.routing import APIRouter
from pydantic.types import UUID4

from api.services import OrdersService, get_orders_service
from metastore import models
from  api.schemas import Order, OrderCreate, OrderDetail

router = APIRouter(prefix="/orders")


@router.get("/", response_model=List[Order])
async def list_orders(
    orders_service: OrdersService = Depends(get_orders_service),
) -> List[models.Order]:
    return orders_service.list()


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: UUID4, orders_service: OrdersService = Depends(get_orders_service)
) -> Optional[models.Order]:
    return orders_service.get(order_id)


@router.post("/", status_code=201, response_model=OrderDetail)
async def create_order(
    order: OrderCreate, orders_service: OrdersService = Depends(get_orders_service)
) -> models.Order:
    return orders_service.create(order)
