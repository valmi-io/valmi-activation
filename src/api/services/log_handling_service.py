'''
Copyright (c) 2023 valmi.io <https://github.com/valmi-io>

Created Date: Thursday, August 17th 2023, 2:02:46 pm
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

from log_handling.log_serving_process import LogServingProcess
from log_handling.log_retriever import LogRetrieverTask
import multiprocessing
import asyncio

class LogHandlingService():
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(LogHandlingService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if LogHandlingService.__initialized:
            return
        
        LogHandlingService.__initialized = True
        
        multiprocessing.set_start_method("spawn", force=True)
        self.mgr = multiprocessing.Manager()
        self.result_dict = self.mgr.dict()
        self.task_queue = multiprocessing.JoinableQueue()
        self.exit_flag_event = multiprocessing.Event()

        self.log_serving_process = LogServingProcess(task_queue=self.task_queue,
                                                     result_dict=self.result_dict, exit_flag_event=self.exit_flag_event)
        self.log_serving_process.start()

    def exit_log_serving_process(self):
        self.log_serving_process.exit_flag_event.set()
        self.log_serving_process.join()

    def add_log_retriever_task(self, log_retriever_task: LogRetrieverTask):
        self.log_serving_process.task_queue.put(log_retriever_task)

    async def read_log_retriever_data(self, log_retriever_task: LogRetrieverTask):
        while self.log_serving_process.is_alive():
            if (str(log_retriever_task) not in self.log_serving_process.result_dict):
                await asyncio.sleep(0.5)
            else:
                return self.log_serving_process.result_dict[str(log_retriever_task)]

        raise Exception("Log Serving Process is not alive!")
