import os
import requests

def question_to_sql(question: str) -> str:
    prompt = f"Convert the following question into an SQL query:{question}"
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
    sql = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return sql
