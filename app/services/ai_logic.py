import os
import sqlite3
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY, DB_PATH
import matplotlib.pyplot as plt
import io
import base64

from app.core.logger import app_logger, sql_logger

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")


def get_schema_info():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_info = ""
        for (table_name,) in tables:
            schema_info += f"Table: {table_name}\n"
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                schema_info += f" - {col[1]} ({col[2]})\n"
            schema_info += "\n"

        conn.close()
        return schema_info

    except Exception as e:
        app_logger.error(f"[Schema Fetch Error] {e}")
        raise


def generate_chart(columns, data):
    if len(columns) >= 2 and len(data) > 0:
        x_values = [str(row[0]) for row in data]
        y_values = [row[1] for row in data]

        plt.figure(figsize=(8, 5))
        plt.bar(x_values, y_values)
        plt.xlabel(columns[0])
        plt.ylabel(columns[1])
        plt.title("Chart")
        plt.xticks(rotation=45)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        chart_base64 = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close()
        return chart_base64
    return None


async def handle_question(question: str):
    schema = get_schema_info()

    prompt = f"""
You are a precise and careful AI assistant that writes SQL queries for a SQLite database.

Below is the exact database schema. Use it **strictly** and **do not assume** anything not explicitly listed.

{schema}

IMPORTANT GUIDELINES:
- Only use table and column names **exactly as they appear** above.
- Never guess, pluralize, singularize, or invent table/column names.
- Do **not** reverse table and column names.
- If a name does not appear in the schema, **do not use it**.
- The correct table is `total_sales`, and the column is `total_sale`. Do not invert or modify these.
- If unsure, say so or return an error.

EXAMPLE:
Q: What is the total sale amount?
A: SELECT SUM(total_sale) FROM total_sales;

Q: What is my total sales ?
A: SELECT SUM(total_sale) FROM total_sales;

Now write a SQL query to answer the following user question:
\"\"\"{question}\"\"\"

Only return the SQL query — no explanations, markdown, or formatting.
"""


    try:
        response = model.generate_content([{"text": prompt}])
        sql_query = response.text.strip().strip("```sql").strip("```")

        # Log the question and SQL query
        sql_logger.info(f"Question: {question}")
        sql_logger.info(f"Generated SQL: {sql_query}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()

        sql_logger.info(f"Returned {len(rows)} rows with columns: {columns}")

        chart = generate_chart(columns, rows)

        return {
            "query": sql_query,
            "columns": columns,
            "answer": rows,
            "chart": chart
        }

    except Exception as e:
        app_logger.error(f"[AI Logic Error] Question: {question} | {str(e)}")
        return {
            "error": str(e),
            "query": sql_query if 'sql_query' in locals() else None
        }
