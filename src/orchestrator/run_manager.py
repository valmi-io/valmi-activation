"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Tuesday, March 21st 2023, 6:56:23 pm
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

# TODO: Listen to Sources and Destinations for Control Messsages Like Oauth refreshes| Destination unreachable | Source unreachable
# TODO: OAUTH refreshes should be done by the api Server (its responsibility is crendential management & configuration). This server is responsible for (job run & meta data management).
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
from dagster_graphql import DagsterGraphQLClientError
from sqlalchemy.orm.attributes import flag_modified

logger = logging.getLogger(v.get("LOGGER_NAME"))
TICK_INTERVAL = 1


class SyncRunnerThread(threading.Thread):
    def __init__(self, thread_id: int, name: str, dagster_client: ValmiDagsterClient) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.exit_flag = False
        self.name = name
        self.dc = dagster_client

        db_session = next(get_session())
        self.sync_service = get_syncs_service(db_session)
        self.run_service = get_sync_runs_service(db_session)

    def abort_active_run(self, sync, run):
        dagster_run_id = run.dagster_run_id

        run_status = self.dc.get_run_status(dagster_run_id)
        if run_status == DagsterRunStatus.STARTED \
            or run_status == DagsterRunStatus.STARTING \
                or run_status == DagsterRunStatus.QUEUED:

            self.dc.terminate_run(dagster_run_id)

            sync.run_status = SyncStatus.STOPPED
            run.status = SyncStatus.STOPPED
            self.sync_service.update_sync_and_run(sync, run)
        else:
            logger.error(f"Cannot abort the run with state '{run_status}'")

    @exception_to_sys_exit
    def _run(self):
        while not self.exit_flag:
            time.sleep(TICK_INTERVAL)

            from orchestrator.job_generator import repo_ready

            if not repo_ready:
                continue

            try:
                syncs_to_handle = self.sync_service.get_syncs_to_run()
                # print(syncs_to_handle)

                for sync in syncs_to_handle:
                    if sync.status != SyncConfigStatus.ACTIVE:
                        run = self.run_service.get(sync.last_run_id)
                        # Set connector run_manager status to terminated to stop source and destination connections
                        run_status = {
                            "status": "terminated",
                            "message": f"Run aborted because syn status is {sync.status}",
                        }
                        self.run_service.update_sync_run_extra_data(
                            sync.last_run_id, "run_manager", "status", run_status)
                        self.abort_active_run(sync, run)
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

                    elif sync.run_status == SyncStatus.ABORTING:
                        run = self.run_service.get(sync.last_run_id)
                        self.abort_active_run(sync, run)
                    elif sync.run_status == SyncStatus.SCHEDULED:
                        # submit job to dagster,
                        # TODO: if jobs is already submitted, but failed to set metastore status, check below TODO
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

                        except DagsterGraphQLClientError as e:
                            if "JobNotFoundError" in str(e):
                                logger.warning("Job not found for sync %s", sync.sync_id)
                            else:
                                raise

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
                            error_msg = None
                            status = "success"
                            keys_to_check = ["src", "dest"]
                            for key in keys_to_check:
                                if (
                                    run.extra is not None
                                    and key in run.extra.keys()
                                    and "status" in run.extra[key].keys()
                                ):
                                    if run.extra[key]["status"]["status"] == "failed":
                                        sync.run_status = SyncStatus.FAILED
                                        run.status = SyncStatus.FAILED
                                        status = "failed"
                                        error_msg = run.extra[key]["status"]["message"]
                                        break

                            if error_msg is None:
                                sync.run_status = SyncStatus.STOPPED
                                run.status = SyncStatus.STOPPED

                            run_status = {"status": status, "message": error_msg}

                            if not run.extra:
                                run.extra = {}
                            if "run_manager" not in run.extra:
                                run.extra["run_manager"] = {}
                            run.extra["run_manager"]["status"] = run_status
                            flag_modified(run, "extra")
                            flag_modified(run, "status")

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
                            flag_modified(run, "status")

                            update_db = True
                        if update_db:
                            self.sync_service.update_sync_and_run(sync, run)
            except Exception:
                logger.exception("Error while handling syncs in run manager")
                raise

    def run(self) -> None:
        self._run()
