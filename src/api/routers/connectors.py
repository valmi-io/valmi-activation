import io
import json
import logging
import os
import shlex
import subprocess
import uuid

from fastapi import Response
from fastapi.routing import APIRouter
from vyper import v

from api.schemas import DockerItem
from api.schemas.connector import ConnectorConfig

router = APIRouter(prefix="/connectors")

logger = logging.getLogger(v.get("LOGGER_NAME"))


@router.post("/{connector_type}/spec", response_model=str)
async def get_source_spec(connector_type: str, docker_item: DockerItem) -> str:
    logger.debug("Getting spec for source: %s", connector_type)
    lines = []
    proc = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "{0}:{1}".format(docker_item.docker_image, docker_item.docker_tag),
            "spec",
        ],
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        lines.append(line)
    return Response(content="".join(lines))


@router.post("/{connector_type}/check", response_model=str)
async def source_check(connector_type: str, config: ConnectorConfig) -> str:
    logger.debug("Checking  config: %s", connector_type)
    newid: str = str(uuid.uuid4())

    # filename: str = "/tmp/{0}/config.json".format(newid)
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open("/tmp/shared_dir/{0}".format(newid), "w") as f:
        f.write(json.dumps(config.config))
    lines = []
    args = shlex.split(
        "docker run --network host \
            --rm -v /tmp/shared_dir/{0}:/secrets/config.json \
                {1}:{2} check --config /secrets/config.json".format(
            newid, config.docker_image, config.docker_tag
        )
    )
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        lines.append(line)

    # shutil.rmtree("/tmp/{0}".format(newid))
    os.unlink("/tmp/shared_dir/{0}".format(newid))
    return Response(content="".join(lines))
