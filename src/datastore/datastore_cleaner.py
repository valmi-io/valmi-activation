from datetime import datetime, timedelta
import logging
import shutil
import threading
import time

import os
from os.path import join
from vyper import v
from api.services import get_sync_runs_service
from metastore.session import get_session
from orchestrator.job_generator import SHARED_DIR

logger = logging.getLogger(v.get("LOGGER_NAME"))


class DatastoreCleaner:
    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(DatastoreCleaner, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.cleaner_thread = DatastoreCleanerThread(32, "DatastoreCleanerThread")
        self.cleaner_thread.start()

    def destroy(self) -> None:
        self.cleaner_thread.exitFlag = True


class DatastoreCleanerThread(threading.Thread):
    def __init__(self, threadID: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.exitFlag = False
        self.name = name

        dbSession = next(get_session())
        self.run_service = get_sync_runs_service(dbSession)

    def run(self) -> None:
        while not self.exitFlag:
            try:
                logger.info("Cleaning all datastore ")

                runs = self.run_service.get_active_and_latest_runs(
                    after=datetime.now() - timedelta(seconds=v.get("DATASTORE_CLEAN_UNTIL") or 60)
                )

                store_path = join(SHARED_DIR, "intermediate_store")
                dirlist = os.listdir(store_path)

                logger.debug("runset %s", runs)
                logger.debug("dirlist %s", dirlist)
                pruneset = set(dirlist) - set([run.run_id for run in runs])
                logger.debug("pruneset %s", pruneset)
                for dir in pruneset:
                    dir_path = join(store_path, dir)
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)

                time.sleep(v.get_int("DATASTORE_CLEANER_SLEEP_TIME") or 60)
            except Exception:
                logger.exception("Error while cleaned datastore")
                time.sleep(v.get_int("DATASTORE_CLEANER_SLEEP_TIME") or 60)
