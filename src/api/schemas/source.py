from pydantic import BaseModel

from .utils import to_camel


class DockerItem(BaseModel):
    docker_image: str
    docker_tag: str

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class SourceDockerConfig(DockerItem):
    config_json_str: str
