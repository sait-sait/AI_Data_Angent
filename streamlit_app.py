import streamlit as st
from app.services.ai_logic import handle_question
from app.core.logger import app_logger
import base64
import asyncio

st.set_page_config(page_title="AI Data Agent", layout="wide")

st.title("Ask a Question About Your Data")

question = st.text_input("Ask a question:")

if st.button("Submit") and question.strip():
    app_logger.info(f"User submitted question: '{question}'")

    with st.spinner("Thinking..."):
        try:
            response = asyncio.run(handle_question(question))

            if "error" in response:
                st.error(f"Error: {response['error']}")
                app_logger.error(f"Error while processing question: {response['error']}")
                if response.get("query"):
                    st.text_area("Generated SQL", response["query"], height=100)
                    app_logger.info(f"Generated SQL (error case): {response['query']}")
            else:
                st.success("Query executed successfully!")
                app_logger.info("Query executed successfully.")
                app_logger.info(f"Generated SQL: {response['query']}")

                st.text_area("SQL Query Used", response["query"], height=100)

                if response["columns"] and response["answer"]:
                    st.subheader("Data")
                    st.dataframe(
                        {col: [row[i] for row in response["answer"]] for i, col in enumerate(response["columns"])},
                        use_container_width=True,
                    )
                    app_logger.info(f"Returned {len(response['answer'])} rows.")

                if response.get("chart"):
                    st.subheader("Chart")
                    st.image(base64.b64decode(response["chart"]), use_column_width=True)
                    app_logger.info("Chart rendered successfully.")
        except Exception as e:
            st.error("Something went wrong. Please check logs.")
            app_logger.exception(f"Unhandled exception in Streamlit app: {str(e)}")
