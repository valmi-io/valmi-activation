from pydantic import BaseModel, UUID4
from .utils import to_camel


class MetricBase(BaseModel):
    sync_id: UUID4
    run_id: UUID4

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class MetricCreate(MetricBase):
    chunk_id: UUID4
    connector_id: UUID4
    metrics: dict[str, int]


class Metric(MetricCreate):
    pass
