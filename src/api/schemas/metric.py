from pydantic import BaseModel, UUID4
from .utils import to_camel


class MetricBase(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class MetricCreate(MetricBase):
    sync_id: UUID4
    connector_id: UUID4
    run_id: UUID4
    chunk_id: UUID4
    metrics: dict[str, str | int]


class Metric(MetricCreate):
    pass
