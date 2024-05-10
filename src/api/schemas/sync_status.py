from pydantic import BaseModel
from enum import Enum

class LastSyncStatus(BaseModel):
    status: str
