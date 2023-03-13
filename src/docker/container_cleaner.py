import logging
import os
import threading
import time

from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))


class ContainerCleaner:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(ContainerCleaner, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.cleaner_thread = ContainerCleanerThread(16, "ContainerCleanerThread")
        self.cleaner_thread.start()

    def destroy(self) -> None:
        self.cleaner_thread.exitFlag = True


class ContainerCleanerThread(threading.Thread):
    def __init__(self, threadID: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name

    def run(self) -> None:
        while not self.exitFlag:
            try:
                logger.info("Cleaning all exited Docker Containers")
                os.system(
                    f'docker container prune --force --filter "label=io.valmi.name" \
                        --filter until={v.get("DOCKER_CONTAINER_CLEAN_UNTIL") or "1m"}'
                )
                time.sleep(v.get_int("DOCKER_CONTAINER_CLEANER_SLEEP_TIME") or 60)
            except Exception:
                logger.exception("Error while cleaning docker containers")
