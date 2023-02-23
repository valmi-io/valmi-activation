import logging
import threading
import time

import requests
from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))


class JobCreatorThread(threading.Thread):
    def __init__(self, threadID: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name

    def run(self) -> None:
        while not self.exitFlag:
            print("Starting " + self.name)
            try:
                resp = requests.get(f"http://{v.get('APP_BACKEND')}:{v.get('APP_BACKEND_PORT')}/api/v1/auth/syncs")
                with open("/tmp/syncs.json", "r") as f:
                    if (f.read()) != resp.text:
                        logger.info("New syncs found")
                        self.gen_dagster_job_archive(resp.json())
                        with open("/tmp/syncs.json", "w") as replace_file:
                            replace_file.write(resp.text)

            except Exception:
                logger.exception("Error while fetching sync jobs and creating dagster jobs")
            time.sleep(5)

    def gen_dagster_job_archive(self, syncs) -> None:
        pass


class Orchestrator:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(Orchestrator, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.jobCreatorThread = JobCreatorThread(1, "JobCreatorThread")
        self.jobCreatorThread.start()

    def destroy(self) -> None:
        self.jobCreatorThread.exitFlag = True
