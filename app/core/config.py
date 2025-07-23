import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_PATH = os.getenv("DB_PATH")

if not DB_PATH or not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"Database not found at: {DB_PATH}")