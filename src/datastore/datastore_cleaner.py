"""
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Monday, March 13th 2023, 4:48:17 pm
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
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(DatastoreCleaner, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if DatastoreCleaner.__initialized:
            return

        DatastoreCleaner.__initialized = True

        self.cleaner_thread = DatastoreCleanerThread(32, "DatastoreCleanerThread")
        self.cleaner_thread.start()

    def destroy(self) -> None:
        self.cleaner_thread.exit_flag = True


class DatastoreCleanerThread(threading.Thread):
    def __init__(self, thread_id: int, name: str) -> None:
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.exit_flag = False
        self.name = name

        db_session = next(get_session())
        self.run_service = get_sync_runs_service(db_session)

    def run(self) -> None:
        while not self.exit_flag:
            try:
                logger.info("Cleaning all datastore ")

                runs = self.run_service.get_active_or_latest_runs(
                    after=datetime.now() - timedelta(seconds=v.get("DATASTORE_CLEAN_UNTIL") or 60)
                )

                store_path = join(SHARED_DIR, "intermediate_store")
                dirlist = os.listdir(store_path)

                logger.debug("runset %s", [run.run_id for run in runs])
                logger.debug("dirlist %s", dirlist)
                pruneset = set(dirlist) - set([str(run.run_id) for run in runs])
                logger.debug("pruneset %s", pruneset)
                for dir in pruneset:
                    dir_path = join(store_path, dir)
                    if os.path.exists(dir_path):
                        shutil.rmtree(dir_path)

                time.sleep(v.get_int("DATASTORE_CLEANER_SLEEP_TIME") or 60)
            except Exception:
                logger.exception("Error while cleaned datastore")
                time.sleep(v.get_int("DATASTORE_CLEANER_SLEEP_TIME") or 60)
