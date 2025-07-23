import os
import sqlite3
import uuid
import google.generativeai as genai
import matplotlib.pyplot as plt
import io
import base64

from app.core.config import GEMINI_API_KEY, DB_PATH

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

# Directory to save charts
CHART_DIR = "app/static/charts"
os.makedirs(CHART_DIR, exist_ok=True)


def get_schema_info():
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


"""def generate_chart(data, chart_type="bar"):
    # Generate a unique filename
    chart_path = os.path.join(CHART_DIR, f"{uuid.uuid4().hex}.png")

    # Assume first column = x, second = y
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
    plt.savefig(chart_path)
    plt.close()

    return chart_path
    """
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
You are a helpful AI assistant that writes SQL queries for a SQLite database.

Here is the database schema:
{schema}

Now write a SQL query that answers the following question:
\"\"\"{question}\"\"\"

Only return the SQL query. Do not include explanations or markdown.
    """

    response = model.generate_content([{"text": prompt}])
    sql_query = response.text.strip().strip("```sql").strip("```")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()

        # Format results
        """if len(rows) == 1 and len(rows[0]) == 1:
            return {"answer": f"{rows[0][0]:,.2f}", "query": sql_query}

        chart_path = None
        if rows and len(rows[0]) >= 2:
            chart_path = generate_chart(rows)
            chart_url = f"/static/charts/{os.path.basename(chart_path)}"
        else:
            chart_url = None

        return {
            "answer": rows,
            "columns": column_names,
            "query": sql_query,
            "chart": chart_url,
        }"""
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
        return {"error": str(e), "query": sql_query}
