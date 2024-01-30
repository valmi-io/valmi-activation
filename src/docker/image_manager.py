"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, March 9th 2023, 8:58:22 pm
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

import logging
import os
import threading
import time
import requests
from requests.auth import HTTPBasicAuth
from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))


class ImageWarmupManager:
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(ImageWarmupManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if ImageWarmupManager.__initialized:
            return

        ImageWarmupManager.__initialized = True

        self.image_warmup_thread = DockerImageWarmupThread(64, "DockerImageWarmupThread")
        self.image_warmup_thread.start()

    def destroy(self) -> None:
        self.image_warmup_thread.exit_flag = True


class DockerImageWarmupThread(threading.Thread):
    def __init__(self, thread_id: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.exit_flag = False
        self.name = name

    def run(self) -> None:
        while not self.exit_flag:
            try:
                logger.info("Pulling all Docker Container images")
                resp = requests.get(
                    f"http://{v.get('APP_BACKEND')}:{v.get('APP_BACKEND_PORT')}/api/v1/superuser/connectors/",
                    timeout=v.get("HTTP_REQ_TIMEOUT"),
                    auth=HTTPBasicAuth(v.get("ADMIN_EMAIL"), v.get("ADMIN_PASSWORD")),
                )
                connector_roles = ["SRC", "DEST"]

                json_resp = resp.json()
                for role in connector_roles:
                    for typ in json_resp[role]:
                        img = typ["docker_image"]
                        tag = typ["docker_tag"]
                        os.system(
                            f"docker inspect --type=image {img}:{tag} >> /dev/null; \
                                ret_val=$?; \
                                if [ $ret_val -ne 0 ]; \
                                    then docker pull {img}:{tag} ;\
                                fi"
                        )
                time.sleep(v.get_int("DOCKER_IMAGE_MANAGER_SLEEP_TIME") or 60)
            except Exception:
                logger.exception("Error while pulling images")
                time.sleep(v.get_int("DOCKER_IMAGE_MANAGER_SLEEP_TIME") or 60)
