from typing import Optional
from pydantic import BaseModel, Extra


class RunTimeArgs(BaseModel):
    http_timeout: Optional[int] = 3
    max_retries: Optional[int] = 3
    records_per_metric: Optional[int] = 10
    chunk_size: Optional[int] = 300  # Make sure chunk_size  is a multiple of records_per_metric

    class Config:
        extra = Extra.allow
