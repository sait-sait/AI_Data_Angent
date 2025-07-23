import streamlit as st
from app.services.ai_logic import handle_question
import base64
import asyncio

st.set_page_config(page_title="AI Data Agent", layout="wide")

st.title("💡 Ask a Question About Your Data")

question = st.text_input("Ask a question:")

if st.button("Submit") and question.strip():
    with st.spinner("Thinking..."):
        response = asyncio.run(handle_question(question))

    if "error" in response:
        st.error(f"Error: {response['error']}")
        if response.get("query"):
            st.text_area("Generated SQL", response["query"], height=100)
    else:
        st.success("Query executed successfully!")

        st.text_area("SQL Query Used", response["query"], height=100)

        if response["columns"] and response["answer"]:
            st.subheader("Data")
            st.dataframe(
                {col: [row[i] for row in response["answer"]] for i, col in enumerate(response["columns"])},
                use_container_width=True,
            )

        if response.get("chart"):
            st.subheader("Chart")
            st.image(base64.b64decode(response["chart"]), use_column_width=True)
