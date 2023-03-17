from typing import Dict
from pydantic import BaseModel


class DockerItem(BaseModel):
    docker_image: str
    docker_tag: str

    class Config:
        allow_population_by_field_name = True


class ConnectorConfig(DockerItem):
    config: Dict
