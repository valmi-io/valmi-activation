# Provide API for the connectors to save source and destination checkpoints

# Handles failures and retries
# Provide Pull API for Synchronising the source and destination. And even sources and destinations ask whether to fail or continue.
# Listen to Sources and Destinations for Control Messsages Like Oauth refreshes| Destination unreachable | Source unreachable
# OAUTH refreshes should be done by the api Server (its responsibility is crendential management & configuration). This server is responsible for (job run & meta data management).
import logging
import threading
import time
import uuid
from api.services import get_syncs_service, get_sync_runs_service
from metastore.session import get_session
from vyper import v
from metastore.models import SyncStatus, SyncConfigStatus
from api.schemas import SyncRunCreate
from datetime import datetime
from dagster import DagsterRunStatus
from utils.retry_decorators import exception_to_sys_exit
from .dagster_client import ValmiDagsterClient
from sqlalchemy.orm.attributes import flag_modified

logger = logging.getLogger(v.get("LOGGER_NAME"))
TICK_INTERVAL = 5


class SyncRunnerThread(threading.Thread):
    def __init__(self, threadID: int, name: str, dagster_client: ValmiDagsterClient) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name
        self.dc = dagster_client

        dbSession = next(get_session())
        self.sync_service = get_syncs_service(dbSession)
        self.run_service = get_sync_runs_service(dbSession)

    @exception_to_sys_exit
    def _run(self):
        while not self.exitFlag:
            time.sleep(TICK_INTERVAL)

            from orchestrator.job_generator import repo_ready

            if not repo_ready:
                continue

            try:
                syncs_to_handle = self.sync_service.get_syncs_to_run()
                print(syncs_to_handle)

                for sync in syncs_to_handle:
                    if sync.status != SyncConfigStatus.ACTIVE:
                        # TODO: terminate dagster runs
                        pass
                    elif sync.run_status == SyncStatus.STOPPED:
                        logger.info("Sync is stopped %s", sync.sync_id)

                        run = SyncRunCreate(
                            run_id=uuid.uuid4(),
                            sync_id=sync.sync_id,
                            run_at=datetime.now(),
                            status=SyncStatus.SCHEDULED,
                        )

                        sync.last_run_at = run.run_at
                        sync.run_status = SyncStatus.SCHEDULED
                        sync.last_run_id = run.run_id

                        self.sync_service.update_sync_and_create_run(sync, run)

                    elif sync.run_status == SyncStatus.FAILED:
                        # TODO: check if retry is needed, else set it to stopped
                        run = self.run_service.get(sync.last_run_id)

                        sync.run_status = SyncStatus.STOPPED
                        run.status = SyncStatus.STOPPED
                        self.sync_service.update_sync_and_run(sync, run)

                    elif sync.run_status == SyncStatus.SCHEDULED:
                        # submit job to dagster,
                        # TODO: if already submitted, but failed to set metastore status, check below TODO
                        try:
                            dagster_run_id = self.dc.submit_job_execution(
                                self.dc.su(sync.sync_id),
                                tags={"sync_id": self.dc.su(sync.sync_id), "run_id": self.dc.su(sync.last_run_id)},
                                # run_config={
                                #    "ops": {"initialise": {"config": {"run_id": self.dc.su(sync.last_run_id)}}}
                                # },
                            )
                            # TODO: saving dagster run id in the metastore, but if it crashes before this.
                            # we will have to handle it.
                            # Python dagster client has no api to obtain dagster run id from job name.
                            # We can use the graphql api to get the dagster run id from the job name.

                            run = self.run_service.get(sync.last_run_id)

                            sync.run_status = SyncStatus.RUNNING
                            run.status = SyncStatus.RUNNING
                            run.dagster_run_id = dagster_run_id

                            self.sync_service.update_sync_and_run(sync, run)

                        except Exception:
                            logger.exception("Error while submitting job to dagster and saving state to metastore")
                            raise

                    elif sync.run_status == SyncStatus.RUNNING:
                        # check dagster status
                        run = self.run_service.get(sync.last_run_id)

                        dagster_run_status = self.dc.get_run_status(run.dagster_run_id)

                        update_db = False
                        if dagster_run_status == DagsterRunStatus.SUCCESS:
                            # TODO: move the following code to run service
                            self.sync_service.db_session.refresh(run)

                            # if either of the source or destination failed, then the sync should be failed.
                            src_status = run.extra["src"]["status"]["status"]
                            dest_status = run.extra["dest"]["status"]["status"]

                            error_msg = None
                            status = "success"
                            if src_status == "failed":
                                error_msg = run.extra["src"]["status"]["message"]
                                status = "failed"

                                sync.run_status = SyncStatus.FAILED
                                run.status = SyncStatus.FAILED
                            elif dest_status == "failed":
                                error_msg = run.extra["dest"]["status"]["message"]
                                status = "failed"

                                sync.run_status = SyncStatus.FAILED
                                run.status = SyncStatus.FAILED
                            else:
                                sync.run_status = SyncStatus.STOPPED
                                run.status = SyncStatus.STOPPED

                            run_status = {"status": status, "message": error_msg}

                            if not run.extra:
                                run.extra = {}
                            if "run_manager" not in run.extra:
                                run.extra["run_manager"] = {}
                            run.extra["run_manager"]["status"] = run_status
                            flag_modified(run, "extra")

                            update_db = True

                        elif (
                            dagster_run_status == DagsterRunStatus.FAILURE
                            or dagster_run_status == DagsterRunStatus.CANCELED
                        ):
                            # TODO: move the following code to run service
                            self.sync_service.db_session.refresh(run)

                            sync.run_status = SyncStatus.FAILED
                            run.status = SyncStatus.FAILED
                            if not run.extra:
                                run.extra = {}
                            if "run_manager" not in run.extra:
                                run.extra["run_manager"] = {}
                            run.extra["run_manager"]["status"] = {"status": "failed", "message": "FILL THIS IN!"}
                            flag_modified(run, "extra")

                            update_db = True
                        if update_db:
                            self.sync_service.update_sync_and_run(sync, run)
            except Exception:
                logger.exception("Error while handling syncs in run manager")
                raise

    def run(self) -> None:
        self._run()
