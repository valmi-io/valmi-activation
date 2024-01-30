"""
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Monday, March 13th 2023, 4:40:57 pm
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
