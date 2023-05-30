from typing import Optional
from pydantic import BaseModel, Extra


class RunTimeArgs(BaseModel):
    http_timeout: Optional[int] = 3
    max_retries: Optional[int] = 3
    records_per_metric: Optional[int] = 10

    # We are corrently creating maxumum of 3 identities per user ( refer : https://developers.google.com/google-ads/api/reference/rpc/v13/UserIdentifier)
    # There are no limits on the number of operations you can add to a single job.
    # However, for optimal processing, we recommend adding up to 10,000 identifiers in a single call to the
    # reference : https://developers.google.com/google-ads/api/docs/remarketing/audience-types/customer-match#customer_match_considerations
    # so chunk_size * 3 < 10000, chunk_size < 3333
    chunk_size: Optional[int] = 3000

    class Config:
        extra = Extra.allow
