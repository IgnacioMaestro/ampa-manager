from datetime import datetime
from typing import Optional

from django.core.management.base import BaseCommand


class LogToFileCommand(BaseCommand):
    LOG_FILE_ENCODING = 'utf-8'
    DATETIME_FORMAT = '%d%m%Y_%H%M%S'

    def __init__(self, log_file_base_name: Optional[str] = None, **kwargs):
        super().__init__(kwargs)

        self.log_file_base_name = log_file_base_name
        self.log_file = None
        self.open_log_file()

    def open_log_file(self):
        self.log_file = open(self.get_log_file_full_name(), "a", encoding=LogToFileCommand.LOG_FILE_ENCODING)

    def error(self, message: str):
        self.log(f'*** ERROR: {message}')

    def warning(self, message: str):
        self.log(f'*** WARNING: {message}')

    def log(self, message: str):
        print(message)
        self.log_file.writelines([message + '\n'])

    def close_log_file(self):
        if self.log_file:
            self.log_file.close()

    def get_log_file_full_name(self):
        return f"{self.log_file_base_name}_{datetime.now().strftime(LogToFileCommand.DATETIME_FORMAT)}.log"
