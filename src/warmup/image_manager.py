import logging
import threading

from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))


class ImageWarmupManager:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(ImageWarmupManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.image_warmup_thread = DockerImageWarmupThread(3, "DockerImageWarmupThread")
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
                # get all connectors from db
                # issue docker pull for each connector
                pass
            except Exception:
                logger.exception("Error while pulling images")
            self.exitFlag = True
