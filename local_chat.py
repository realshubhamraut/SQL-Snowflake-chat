# local_chat.py
from dotenv import load_dotenv
import os
import asyncio
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from sqlalchemy import inspect

# Ensure an event loop exists
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

def init_database(user: str, host: str, port: str, database: str) -> SQLDatabase:
    db_uri = f"postgresql+psycopg2://{user}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

def finalize_sql(query: str) -> str:
    query = query.strip()
    if query.startswith("```"):
        query = query.strip("`").strip()
        if query.lower().startswith("sql"):
            query = query[3:].strip()
    if not query.endswith(";"):
        query += ";"
    return query

def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text

def adjust_label_fontsize(ax, base_font_size=12, rotation_angle=45, tick_threshold=10):
    xticks = ax.get_xticklabels()
    yticks = ax.get_yticklabels()
    n_xticks = len(xticks)
    n_yticks = len(yticks)
    new_font_size = max(6, base_font_size - (max(n_xticks, n_yticks) - 5))
    ax.tick_params(axis='both', labelsize=new_font_size)
    if n_xticks > tick_threshold:
        plt.setp(ax.get_xticklabels(), rotation=rotation_angle, ha='right')
    ax.xaxis.label.set_size(new_font_size)
    ax.yaxis.label.set_size(new_font_size)
    ax.title.set_size(new_font_size + 2)
    plt.tight_layout()

def get_database_info(db: SQLDatabase, sample_limit: int = 1) -> str:
    db_info = "Database Schema and Sample Data:\n"
    try:
        engine = db._engine
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
    except Exception as e:
        db_info += f"(Could not use inspector: {e})\n"
        db_info += db.get_table_info()
        return db_info

    for table in table_names:
        db_info += f"\nTable: {table}\n"
        try:
            columns = inspector.get_columns(table)
            col_info = ", ".join([f"{col['name']} ({col['type']})" for col in columns])
            db_info += f"Columns: {col_info}\n"
        except Exception as e:
            db_info += f"Columns: (Error retrieving columns: {e})\n"
        try:
            sample = db.run(f"SELECT * FROM {table} LIMIT {sample_limit}")
            db_info += f"Sample Data:\n{sample}\n"
        except Exception as e:
            db_info += f"Sample Data: (Could not retrieve sample data: {e})\n"
    return db_info

def get_sql_chain(db):
    template = """
You are a data analyst interacting with a PostgreSQL database.
Below is the dynamic database information (schema and sample data):
{db_info}

Conversation History: {chat_history}

Question: {question}

Write only the SQL query and nothing else.
SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
    return (
        RunnablePassthrough.assign(db_info=lambda _: get_database_info(db))
        | prompt
        | llm
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    template = """
You are a data analyst interacting with a PostgreSQL database.
Below is the dynamic database information (schema and sample data):
{db_info}

Conversation History: {chat_history}
SQL Query: <SQL>{query}</SQL>
User Question: {question}
SQL Response: {response}

Provide your answer in markdown format.
    """
    prompt_chain = ChatPromptTemplate.from_template(template)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
    chain = (
        RunnablePassthrough.assign(query=sql_chain)
        .assign(
            db_info=lambda _: get_database_info(db),
            response=lambda vars: db.run(finalize_sql(vars["query"]))
        )
        | prompt_chain
        | llm
        | StrOutputParser()
    )
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history[-5:],
    })

def get_visualization_data(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    sql_query_text = sql_chain.invoke({
         "question": user_query,
         "chat_history": chat_history[-5:]
    })
    cleaned_query = finalize_sql(sql_query_text)
    engine = db._engine
    try:
        df = pd.read_sql(cleaned_query, engine)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        df = pd.DataFrame()
    return df, cleaned_query

def get_response_with_sql(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    sql_query_text = sql_chain.invoke({
         "question": user_query,
         "chat_history": chat_history[-5:]
    })
    cleaned_query = finalize_sql(sql_query_text)
    natural_language_response = get_response(user_query, db, chat_history)
    return natural_language_response, cleaned_query

# --- Simple chat UI for Local PostgreSQL ---
def run_chat():
    st.markdown("### Local PostgreSQL Chat")
    if "local_chat_history" not in st.session_state:
        st.session_state["local_chat_history"] = []
    for msg in st.session_state["local_chat_history"]:
        if msg["role"] == "user":
            st.markdown(f"**User:** {msg['content']}")
        else:
            st.markdown(f"**Assistant:** {msg['content']}")
    user_input = st.chat_input("Type a message for PostgreSQL:")
    if user_input:
        st.session_state["local_chat_history"].append({"role": "user", "content": user_input})
        if "db" in st.session_state:
            if any(keyword in user_input.lower() for keyword in ["chart", "plot", "visualize", "graph"]):
                df, sql_used = get_visualization_data(user_input, st.session_state.db, st.session_state["local_chat_history"])
                if df.empty:
                    response = "No data returned or error occurred."
                else:
                    fig, ax = plt.subplots(figsize=(5,5), dpi=100)
                    if "line" in user_input.lower():
                        if df.shape[1] >= 2:
                            ax.plot(df.iloc[:,0], df.iloc[:,1], marker='o')
                            ax.set_xlabel(df.columns[0])
                            ax.set_ylabel(df.columns[1])
                            ax.set_title("Line Chart")
                            adjust_label_fontsize(ax)
                            st.pyplot(fig)
                        else:
                            st.write("Not enough columns for a line chart.")
                    elif "bar" in user_input.lower():
                        if df.shape[1] >= 2:
                            ax.bar(df.iloc[:,0], df.iloc[:,1])
                            ax.set_xlabel(df.columns[0])
                            ax.set_ylabel(df.columns[1])
                            ax.set_title("Bar Chart")
                            adjust_label_fontsize(ax)
                            st.pyplot(fig)
                        else:
                            st.write("Not enough columns for a bar chart.")
                    else:
                        st.dataframe(df)
                    st.markdown("**SQL Query used:** `" + sql_used + "`")
                    response = "Displayed visualization for your query."
            else:
                resp, sql_used = get_response_with_sql(user_input, st.session_state.db, st.session_state["local_chat_history"])
                resp = strip_code_fences(resp)
                st.markdown(resp)
                st.markdown("**SQL Query used:** `" + sql_used + "`")
                response = resp
            st.session_state["local_chat_history"].append({"role": "assistant", "content": response})
            st.experimental_rerun()
