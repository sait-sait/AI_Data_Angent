# logger.py

import logging
import os
from datetime import datetime


logs_dir = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_dir, exist_ok=True)


LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

SQL_LOG_FILE_PATH = os.path.join(logs_dir, "sql_queries.log")

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
app_logger = logging.getLogger("app_logger")

sql_logger = logging.getLogger("sql_logger")
sql_handler = logging.FileHandler(SQL_LOG_FILE_PATH)
sql_formatter = logging.Formatter("[%(asctime)s] %(message)s")
sql_handler.setFormatter(sql_formatter)
sql_logger.addHandler(sql_handler)
sql_logger.setLevel(logging.INFO)
