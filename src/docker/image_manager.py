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
        self.image_warmup_thread.exitFlag = True


class DockerImageWarmupThread(threading.Thread):
    def __init__(self, threadID: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name

    def run(self) -> None:
        while not self.exitFlag:
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
