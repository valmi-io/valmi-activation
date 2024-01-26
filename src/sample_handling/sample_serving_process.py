'''
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, August 23rd 2023, 1:40:48 pm
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
'''

import multiprocessing
from vyperconfig import setup_vyper
import logging
from vyper import v
import threading
from multiprocessing import Event, Queue
from queue import Empty
import os
import logging.config


class SampleServingProcess(multiprocessing.Process):
    exit_flag = False

    class ExitFlagListenerThread(threading.Thread):
        def __init__(self, thread_id: int, name: str, exit_flag_event: Event, logger) -> None:
            threading.Thread.__init__(self)
            self.thread_id = thread_id
            self.exit_flag = False
            self.name = name
            self.exit_flag_event = exit_flag_event
            self.logger = logger

        def wait_for_exit_event(self):
            self.logger.info("Waiting for exit flag to be set")
            self.exit_flag_event.wait()
            SampleServingProcess.exit_flag = True
            self.logger.info("Exit Flag: e.is_set()-> %s", self.exit_flag_event.is_set())

        def run(self) -> None:
            self.wait_for_exit_event()

    def __init__(self, task_queue, result_dict, exit_flag_event):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_dict = result_dict
        self.exit_flag_event = exit_flag_event

    def run(self):
        setup_vyper()
        logging.config.dictConfig(v.get("LOGGING_CONF"))
        self.logger = logging.getLogger(v.get("LOGGER_NAME"))

        # Start a thread to listen for the exit flag
        self.exit_flag_thread = SampleServingProcess.ExitFlagListenerThread(
            1, "ExitFlagListenerThread", self.exit_flag_event, self.logger)
        self.exit_flag_thread.start()
        proc_name = self.name
        while True:
            next_task = None
            while True:
                try:
                    next_task = self.task_queue.get(block=True, timeout=1)
                except Empty:
                    if SampleServingProcess.exit_flag is True:
                        break
                else:
                    break
            self.logger.info("found a task")
            if SampleServingProcess.exit_flag is True:
                self.logger.info('%s: Exiting' % proc_name)
                if next_task:
                    self.task_queue.task_done()
                break
            self.logger.info('%s: %s' % (proc_name, next_task))
            try:
                answer = next_task()
            except:
                self.logger.exception("Exception occurred while processing task")
                answer = None
                pass
            self.result_dict[str(next_task)] = answer

            self.task_queue.task_done()
