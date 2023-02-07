from datetime import datetime

from pydantic import BaseModel, NoneStr


class User(BaseModel):
    name: str
