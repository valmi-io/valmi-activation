'''
Copyright (c) 2024 valmi.io <https://github.com/valmi-io>

Created Date: Wednesday, August 23rd 2023, 2:45:49 pm
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

from sample_handling.sample_serving_process import SampleServingProcess
from sample_handling.sample_retriever import SampleRetrieverTask
import multiprocessing
import asyncio


class SampleHandlingService():
    __initialized = False

    def __new__(cls) -> object:
        if not hasattr(cls, "instance"):
            cls.instance = super(SampleHandlingService, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if SampleHandlingService.__initialized:
            return
        
        SampleHandlingService.__initialized = True
        
        multiprocessing.set_start_method("spawn", force=True)
        self.mgr = multiprocessing.Manager()
        self.result_dict = self.mgr.dict()
        self.task_queue = multiprocessing.JoinableQueue()
        self.exit_flag_event = multiprocessing.Event()

        self.sample_serving_process = SampleServingProcess(task_queue=self.task_queue,
                                                           result_dict=self.result_dict, exit_flag_event=self.exit_flag_event)
        self.sample_serving_process.start()

    def exit_sample_serving_process(self):
        self.sample_serving_process.exit_flag_event.set()
        self.sample_serving_process.join()

    def add_sample_retriever_task(self, sample_retriever_task: SampleRetrieverTask):
        self.sample_serving_process.task_queue.put(sample_retriever_task)

    async def read_sample_retriever_data(self, sample_retriever_task: SampleRetrieverTask):
        while self.sample_serving_process.is_alive():
            if (str(sample_retriever_task) not in self.sample_serving_process.result_dict):
                await asyncio.sleep(0.5)
            else:
                response = self.sample_serving_process.result_dict[str(sample_retriever_task)]
                del self.sample_serving_process.result_dict[str(sample_retriever_task)]
                return response

        raise Exception("Sample Serving Process is not alive!")
