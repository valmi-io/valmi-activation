from pydantic import BaseModel, UUID4, Extra


class MetricBase(BaseModel):
    sync_id: UUID4
    run_id: UUID4

    class Config:
        allow_population_by_field_name = True


class MetricCreate(MetricBase):
    chunk_id: int
    connector_id: str
    metrics: dict[str, int]

    class Config:
        extra = Extra.allow


class Metric(MetricCreate):
    pass
