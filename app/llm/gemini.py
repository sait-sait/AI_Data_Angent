import os
import requests
from app.core.logger import logging 
from app.core.exception import CustomException
import sys

def question_to_sql(question: str) -> str:
    try:
        prompt = f"Convert the following question into an SQL query: {question}"
        logging.info(f"Sending prompt to Gemini: {prompt}")

        headers = {
            "Authorization": f"Bearer {os.getenv('GEMINI_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers=headers,
            json=data
        )

        # Log status code
        logging.info(f"Gemini API response status: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"Gemini API Error: {response.text}")
            raise Exception(f"Gemini API returned {response.status_code}: {response.text}")

        sql = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        logging.info(f"Generated SQL: {sql.strip()}")

        return sql.strip()

    except Exception as e:
        logging.exception("Failed to convert question to SQL")
        raise CustomException(e, sys)
