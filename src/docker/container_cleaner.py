import logging
import os
import threading
import time

from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))


class ContainerCleaner:
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(ContainerCleaner, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if ContainerCleaner.__initialized:
            return

        ContainerCleaner.__initialized = True

        self.cleaner_thread = ContainerCleanerThread(16, "ContainerCleanerThread")
        self.cleaner_thread.start()

    def destroy(self) -> None:
        self.cleaner_thread.exit_flag = True


class ContainerCleanerThread(threading.Thread):
    def __init__(self, thread_id: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.exit_flag = False
        self.name = name

    def run(self) -> None:
        while not self.exit_flag:
            try:
                logger.info("Cleaning all exited Docker Containers")
                os.system(
                    f'docker container prune --force --filter "label=io.valmi.version" \
                        --filter until={v.get("DOCKER_CONTAINER_CLEAN_UNTIL") or "10m"}'
                )
                os.system("docker volume prune --force")
                time.sleep(v.get_int("DOCKER_CONTAINER_CLEANER_SLEEP_TIME") or 60)
            except Exception:
                logger.exception("Error while cleaning docker containers")
