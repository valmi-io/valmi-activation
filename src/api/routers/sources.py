import io
import logging
import os
import shlex
import subprocess
import uuid

from fastapi import Response
from fastapi.routing import APIRouter
from vyper import v

from db.schemas import SourceDockerConfig, SourceDockerItem

router = APIRouter(prefix="/sources")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.post("/{source_unique_name}/spec", response_model=str)
async def get_source_spec(source_unique_name: str, docker_item: SourceDockerItem) -> str:
    logger.debug("Getting spec for source: %s", source_unique_name)
    lines = []
    proc = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "{0}:{1}".format(docker_item.source_docker_image, docker_item.source_docker_tag),
            "spec",
        ],
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        lines.append(line)
    return Response(content="".join(lines))


@router.post("/{source_unique_name}/check", response_model=str)
async def source_check(source_unique_name: str, source_config: SourceDockerConfig) -> str:
    logger.debug("Checking source config: %s", source_unique_name)
    newid: str = str(uuid.uuid4())

    # filename: str = "/tmp/{0}/config.json".format(newid)
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open("/tmp/{0}".format(newid), "w") as f:
        f.write(source_config.config_json_str)
    lines = []
    args = shlex.split(
        "docker run --network host --rm -v /tmp/{0}:/secrets/config.json {1}:{2} check --config /secrets/config.json".format(
            newid, source_config.source_docker_image, source_config.source_docker_tag
        )
    )
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        lines.append(line)

    # shutil.rmtree("/tmp/{0}".format(newid))
    os.unlink("/tmp/{0}".format(newid))
    print(" ".join(lines))
    return Response(content="".join(lines))
