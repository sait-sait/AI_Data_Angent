import sys
from app.core.logger import app_logger

def error_message_detail(error, error_detail: sys):
    _, _, exc_tb = error_detail.exc_info()
    line_number = exc_tb.tb_lineno
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = (
        f"Error occurred in Python script [{file_name}] "
        f"line [{line_number}] error message [{str(error)}]"
    )
    return error_message

class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail)
        app_logger.error(self.error_message)

    def __str__(self):
        return self.error_message
