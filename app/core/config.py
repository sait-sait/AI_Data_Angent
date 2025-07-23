import os
from dotenv import load_dotenv
from app.core.logger import logging

# Load environment variables
load_dotenv()
logging.info("Loaded environment variables from .env")

# Get variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = os.getenv("DB_PATH")

# Validate DB path
if not DB_PATH:
    logging.error("DB_PATH is not set in .env")
    raise ValueError("DB_PATH is not set in .env")

if not os.path.exists(DB_PATH):
    logging.error(f"Database not found at path: {DB_PATH}")
    raise FileNotFoundError(f"Database not found at: {DB_PATH}")
else:
    logging.info(f"Database found at: {DB_PATH}")
