import streamlit as st
from modules.nav import nav_bar
from db_processors import NLToPostgresProcessor
from config import CLOUD_SQL_CONNECTION, TABLE_METADATA

def query_page(navigate_to):

    nav_bar()

    st.title("Query Builder")
    st.subheader("Enter your query in natural language")

    processor = NLToPostgresProcessor(
        connection_params=CLOUD_SQL_CONNECTION,
        table_metadata=TABLE_METADATA
    )

    nl_query = st.text_area("Natural Language Query", placeholder = "E.g., Fetch all orders from last month")
    
    if st.button("Generate SQL and Execute", key = "execute_query"):

        if nl_query:
            results = processor.query_db(nl_query)
            display_results(results)  
        else:
            st.error("Please enter a query!")

    if st.button("Logout", key="logout"):
        navigate_to("main")

def display_results(results: dict):

    st.write("**Operation Type:**", results["operation"])
    st.write("**Status:**", results["status"])
    st.write("**Generated SQL Query:**")
    st.code(results["sql_query"], language = "sql")
    
    if results["status"] == "success":

        if results["operation"] == "INSERT":
            st.write("**Inserted Record:**")
            st.write(results.get("created_record", "No record inserted."))
        elif results["operation"] == "READ":
            st.write("**Query Results:**")
            query_results = results.get("results", [])
            if query_results:
                st.table(query_results)
            else:
                st.write("No results found.")
        elif results["operation"] == "UPDATE":
            st.write("**Updated Records:**")
            st.write(results.get("updated_records", "No records updated."))
        elif results["operation"] == "DELETE":
            st.write("**Deleted Records:**")
            st.write(results.get("deleted_records", "No records deleted."))
    else:
        st.error(f"Error: {results.get('message', 'An error occurred.')}")
