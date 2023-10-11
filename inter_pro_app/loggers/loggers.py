import logging
from logging import Logger
import os
from typing import Any

class LoggerGetter:
    loggers: dict[str, Logger] = {}

    def __new__(cls):
        if not(hasattr(LoggerGetter, 'instance')):
            cls.instance = super(LoggerGetter, cls).__new__(cls)
        return cls.instance
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass

    def _init_logger(self, file_name:str, level:int):
        path_to_log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),f'logs/{file_name}.log')
        logger = logging.getLogger(file_name)
        logger.setLevel(level)
        file_handler = logging.FileHandler(path_to_log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        self.loggers[file_name] = logger
    def __str__(self) -> str:
        return f'{self.loggers} | {super().__str__()}'
    def get_logger(self, module_file_name: str, level:int):
        if not (module_file_name in self.loggers.keys()):
            print(f'{module_file_name} not in loggers')
            print(self)
            self._init_logger(module_file_name, level)
        return self.loggers[module_file_name]
        
# loger = LoggerGetter()
# loger2 = LoggerGetter()
# loger.get_logger('asd',logging.INFO)
# print(loger)
# loger.get_logger('asd',logging.INFO)
# print(loger)
# # print(loger2)