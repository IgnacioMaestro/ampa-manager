from datetime import datetime


class Logger:
    DATE_FORMAT = '%d%m%Y_%H%M%S'
    FILE_ENCODING = 'utf-8'

    def __init__(self):
        self.log_file = open(f"import_{datetime.now().strftime(Logger.DATE_FORMAT)}.log", "a", encoding=Logger.FILE_ENCODING)

    def log(self, message):
        print(message)
        self.write_to_log_file(message)
    
    def error(self, message):
        formatted_message = f'*** ERROR: {message}'
        self.log(formatted_message)
    
    def warning(self, message):
        formatted_message = f'*** WARNING: {message}'
        self.log(formatted_message)

    def write_to_log_file(self, message):
        self.log_file.writelines([message])
    
    def close_file(self):
        if self.log_file:
            self.log_file.close()
