"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, March 8th 2023, 11:38:42 am
Author: Rajashekar Varkala @ valmi.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
async def spec(connector_type: str, docker_item: DockerItem) -> str:
    logger.debug("Getting spec for source: %s", connector_type)
    lines = []
    proc = subprocess.Popen(
        [
            "docker",
            "run",
            "{0}:{1}".format(docker_item.docker_image, docker_item.docker_tag),
            "spec",
        ],
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        if line.strip() == "":
            continue
        if json.loads(line)["type"] != "LOG":
            lines.append(line)
    return Response(content="".join(lines))


@router.post("/{connector_type}/check", response_model=str)
async def check(connector_type: str, config: ConnectorConfig) -> str:
    logger.debug("Checking  config: %s", connector_type)
    newid: str = str(uuid.uuid4())

    # filename: str = "/tmp/{0}/config.json".format(newid)
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open("/tmp/shared_dir/{0}".format(newid), "w") as f:
        f.write(json.dumps(config.config))
    lines = []
    args = shlex.split(
        "docker run --network host \
             -v /tmp/shared_dir/{0}:/secrets/config.json \
                {1}:{2} check --config /secrets/config.json".format(
            newid, config.docker_image, config.docker_tag
        )
    )
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        if line.strip() == "":
            continue
        if json.loads(line.encode("utf-8"))["type"] != "LOG":
            lines.append(line)

    # shutil.rmtree("/tmp/{0}".format(newid))
    os.unlink("/tmp/shared_dir/{0}".format(newid))
    return Response(content="".join(lines))


@router.post("/{connector_type}/discover", response_model=str)
async def discover(connector_type: str, config: ConnectorConfig) -> str:
    logger.debug("Discovering connector: %s", connector_type)
    newid: str = str(uuid.uuid4())

    # filename: str = "/tmp/{0}/config.json".format(newid)
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open("/tmp/shared_dir/{0}".format(newid), "w") as f:
        f.write(json.dumps(config.config))
    lines = []
    args = shlex.split(
        "docker run --network host \
            -v /tmp/shared_dir/{0}:/secrets/config.json \
                {1}:{2} discover --config /secrets/config.json".format(
            newid, config.docker_image, config.docker_tag
        )
    )
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
    )
    for line in io.TextIOWrapper(proc.stdout, encoding="utf-8"):  # or another encoding
        if line.strip() == "":
            continue
        if json.loads(line.encode("utf-8"))["type"] != "LOG":
            lines.append(line)

    # shutil.rmtree("/tmp/{0}".format(newid))
    os.unlink("/tmp/shared_dir/{0}".format(newid))
    return Response(content="".join(lines))
