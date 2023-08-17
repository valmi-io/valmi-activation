from log_handling.log_serving_process import LogServingProcess
from log_handling.log_retriever import LogRetrieverTask
import multiprocessing


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
        import logging
        logging.info("Here!!")
        self.log_serving_process.task_queue.put(log_retriever_task)

    def get_log_retriever_task_result(self, log_retriever_task: LogRetrieverTask):
        if (log_retriever_task not in self.log_serving_process.result_dict):
            return None
        return self.log_serving_process.result_dict[log_retriever_task]