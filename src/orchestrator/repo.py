import logging

from vyper import v
from orchestrator.job_generator import JobCreatorThread
from orchestrator.run_manager import SyncRunnerThread
from .dagster_client import ValmiDagsterClient

logger = logging.getLogger(v.get("LOGGER_NAME"))


class Repo:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(Repo, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.client = ValmiDagsterClient(v.get("DAGIT_HOST"), port_number=v.get_int("DAGIT_PORT"))

        self.jobCreatorThread = JobCreatorThread(1, "JobCreatorThread", self.client)
        self.jobCreatorThread.start()

        self.syncRunnerThread = SyncRunnerThread(2, "SyncRunnerThread", self.client)
        self.syncRunnerThread.start()

    def destroy(self) -> None:
        self.jobCreatorThread.exitFlag = True
        self.syncRunnerThread.exitFlag = True
