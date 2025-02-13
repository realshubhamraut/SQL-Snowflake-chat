# tools.py
import streamlit as st
from supabase.client import Client, create_client
from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools import DuckDuckGoSearchRun
from utils.snow_connect import SnowflakeConnection

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
client: Client = create_client(supabase_url, supabase_key)

embeddings = FakeEmbeddings(size=768)

vectorstore = SupabaseVectorStore(
    embedding=embeddings,
    client=client,
    table_name="documents",
    query_name="v_match_documents",
)

retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="Database_Schema",
    description="Search for database schema details",
)

search = DuckDuckGoSearchRun()

def sql_executor_tool(query: str, use_cache: bool = True) -> str:
    conn = SnowflakeConnection()
    return conn.execute_query(query, use_cache)

def retrieve_data(query: str) -> str:
    return sql_executor_tool(query, use_cache=True)
