import os
import sqlite3
import uuid
import google.generativeai as genai
import matplotlib.pyplot as plt
import io
import base64

from app.core.config import GEMINI_API_KEY, DB_PATH
from app.core.logger import app_logger, sql_logger

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

CHART_DIR = "app/static/charts"
os.makedirs(CHART_DIR, exist_ok=True)


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
        app_logger.error(f"Error getting schema info: {e}")
        raise


def generate_chart_base64(data, chart_type="bar"):
    x = [str(row[0]) for row in data]
    y = [row[1] for row in data]

    plt.figure(figsize=(10, 6))
    if chart_type == "line":
        plt.plot(x, y, marker="o")
    else:
        plt.bar(x, y)

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Query Result Visualization")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"


async def handle_question(question: str):
    schema = get_schema_info()

    prompt = f"""
You are a precise AI that writes SQL queries for a SQLite database.

Below is the full database schema. Only use the exact table and column names provided.

{schema}

GUIDELINES:
- NEVER guess or invent table or column names.
- NEVER pluralize or singularize names. Use them **exactly** as shown.
- If a column or table isn't present in the schema, do not use it.
- Always write syntactically valid SQL that works in SQLite.
- DO NOT say you cannot answer unless truly impossible.
- You do not need to generate charts. Just write SQL that returns the data needed to plot a chart in Python.
- If the user asks for a chart or graph, simply return a query that returns the appropriate columns (e.g., product, value) for plotting.
- You may use ORDER BY, LIMIT, JOIN, GROUP BY, etc., based on the schema.

EXAMPLE:
Q: Show total sale for each product as a bar chart.
A: SELECT product_name, SUM(total_sale) AS total_sale FROM total_sales GROUP BY product_name ORDER BY total_sale DESC;

Now write a SQL query for the following user request:
\"\"\"{question}\"\"\"

Only return the SQL query. Do not include explanations, markdown, or comments.
"""


    try:
        response = model.generate_content([{"text": prompt}])
        sql_query = response.text.strip().strip("```sql").strip("```")

        # Log the SQL generation
        sql_logger.info(f"Question: {question}")
        sql_logger.info(f"Generated SQL: {sql_query}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        conn.close()

        sql_logger.info(f"Returned {len(rows)} rows with columns: {column_names}")

        chart_url = None
        if rows and len(rows[0]) >= 2:
            chart_url = generate_chart_base64(rows)

        return {
            "answer": rows,
            "columns": column_names,
            "query": sql_query,
            "chart": chart_url,
        }

    except Exception as e:
        app_logger.error(f"Error handling question: {question} | {e}")
        return {"error": str(e), "query": sql_query if 'sql_query' in locals() else None}
