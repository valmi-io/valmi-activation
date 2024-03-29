import logging

from vyper import v
from orchestrator.job_generator import JobCreatorThread
from orchestrator.run_manager import SyncRunnerThread
from .dagster_client import ValmiDagsterClient
from api.services import get_syncs_service, get_sync_runs_service
from metastore.session import get_session

logger = logging.getLogger(v.get("LOGGER_NAME"))


class Repo:
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(Repo, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if Repo.__initialized:
            return

        Repo.__initialized = True

        self.client = ValmiDagsterClient(v.get("DAGIT_HOST"), port_number=v.get_int("DAGIT_PORT"))
        self.sync_service = get_syncs_service(next(get_session()))
        self.run_service = get_sync_runs_service(next(get_session()))

        self.jobCreatorThread = JobCreatorThread(1, "JobCreatorThread", self.client, self.sync_service, self.run_service)
        self.jobCreatorThread.start()

        self.syncRunnerThread = SyncRunnerThread(2, "SyncRunnerThread", self.client, self.sync_service, self.run_service)
        self.syncRunnerThread.start()

    def destroy(self) -> None:
        self.jobCreatorThread.exit_flag = True
        self.syncRunnerThread.exit_flag = True
