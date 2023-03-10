import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy_utils import EmailType
from enum import Enum


class SyncConfigStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class SyncStatus(str, Enum):
    STOPPED = "stopped"
    FAILED = "failed"
    RUNNING = "running"
    SCHEDULED = "scheduled"


Base: Any = declarative_base()


class Store(Base):
    __tablename__ = "stores"

    store_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city = sa.Column(sa.Text, nullable=False)
    country = sa.Column(sa.Text, nullable=False)
    currency = sa.Column(sa.String(3), nullable=False)
    domain = sa.Column(sa.Text)
    name = sa.Column(sa.Text, nullable=False)
    phone = sa.Column(sa.Text)
    street = sa.Column(sa.Text, nullable=False)
    zipcode = sa.Column(sa.Text, nullable=False)
    email = sa.Column(EmailType)
    timestamp = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)


class Product(Base):
    __tablename__ = "products"

    product_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id = sa.Column(ForeignKey("stores.store_id"), nullable=False)
    store = relationship("Store", backref="products")
    name = sa.Column(sa.Text, nullable=False)
    price = sa.Column(sa.Numeric(12, 2), nullable=False)
    description = sa.Column(sa.Text)

    __table_args__ = (UniqueConstraint("name", "store_id", name="uix_products"),)


class Order(Base):
    __tablename__ = "orders"

    order_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    items = relationship("OrderItem", backref="order")
    name = sa.Column(sa.Text, nullable=False)

    @hybrid_property
    def total(self):
        return sum(item.product.price * item.quantity for item in self.items)


class OrderItem(Base):
    __tablename__ = "order_items"

    order_id = sa.Column(ForeignKey("orders.order_id"), primary_key=True)
    product_id = sa.Column(ForeignKey("products.product_id"), primary_key=True)
    product = relationship("Product", uselist=False)
    quantity = sa.Column(sa.Integer, nullable=False)


class SyncSchedule(Base):
    __tablename__ = "sync_schedules"

    sync_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    last_run_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    last_run_id = sa.Column(UUID(as_uuid=True), nullable=True)
    run_interval = sa.Column(sa.Integer, nullable=False)
    status = sa.Column(sa.Text, nullable=False)
    run_status = sa.Column(sa.Text, nullable=False, default=SyncStatus.STOPPED)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)


class SyncRun(Base):
    __tablename__ = "sync_runs"

    sync_id = sa.Column(ForeignKey("sync_schedules.sync_id"), nullable=False)
    run_id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    status = sa.Column(sa.Text, nullable=False)
    metrics = sa.Column(sa.JSON, nullable=True)
    remarks = sa.Column(sa.JSON, nullable=True)  # store error messages or anything else
    dagster_run_id = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
