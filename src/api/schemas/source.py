from pydantic import BaseModel

from .utils import to_camel


class SourceDockerItem(BaseModel):
    source_docker_image: str
    source_docker_tag: str

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True


class SourceDockerConfig(SourceDockerItem):
    config_json_str: str
