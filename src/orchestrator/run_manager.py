# Provide API for the connectors to save source and destination checkpoints

# Handles failures and retries
# Provide Pull API for Synchronising the source and destination. And even sources and destinations ask whether to fail or continue.
# Listen to Sources and Destinations for Control Messsages Like Oauth refreshes| Destination unreachable | Source unreachable
# OAUTH refreshes should be done by the api Server (its responsibility is crendential management & configuration). This server is responsible for (job run & meta data management).
import logging
import threading
import time

from vyper import v

logger = logging.getLogger(v.get("LOGGER_NAME"))


class SyncRunnerThread(threading.Thread):
    def __init__(self, threadID: int, name: str, dagster_client) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name
        self.dagster_client = dagster_client

    def run(self) -> None:
        while not self.exitFlag:
            try:
                # Part 2:
                # get_all_running_jobs
                # get status from dagster
                # update metastore accordingly

                # Part 1:
                # get_all_jobs
                # for each_job:
                # if not running and past scheduled time
                # start job dagster client with attached tags
                # update metastore

                pass
            except Exception:
                logger.exception("Error while running jobs")
            time.sleep(5)
