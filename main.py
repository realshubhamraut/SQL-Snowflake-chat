# main.py
import re
import warnings
import streamlit as st
from langchain.schema import HumanMessage, AIMessage
from utils.snowddl import Snowddl
from utils.snowchat_ui import StreamlitUICallbackHandler, message_func

# Import processing functions for Local PostgreSQL branch
from local_chat import (
    init_database as pg_init_database,
    get_response_with_sql as pg_get_response_with_sql,
    get_visualization_data as pg_get_visualization_data,
    strip_code_fences as pg_strip_code_fences,
    adjust_label_fontsize as pg_adjust_label_fontsize,
)

# Import processing functions for Cloud Snowflake branch
from snowflake_chat import (
    init_snowflake_connection,
    get_response_with_sql as sf_get_response_with_sql,
    get_visualization_data as sf_get_visualization_data,
    strip_code_fences as sf_strip_code_fences,
    adjust_label_fontsize as sf_adjust_label_fontsize,
    run_chat as sf_run_chat,
)

warnings.filterwarnings("ignore")
snow_ddl = Snowddl()

# --- Initialize Essential Session State Keys ---
if "model" not in st.session_state:
    st.session_state["model"] = "Gemini Flash 2.0"
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your SQL assistant. Ask me anything about your database."}]
if "db" not in st.session_state:
    st.session_state["db"] = None

# --- Header and Page Configuration ---
gradient_text_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');
.snowchat-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 3em;
  /* Replace the red gradient with a Snowflake-inspired bluish-white gradient */
  background: linear-gradient(90deg, #29B5E8, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 5px rgba(0,0,0,0.2);
  margin: 0;
  padding: 20px 0;
  text-align: center;
}
</style>
<div class="snowchat-title">SQL Snowflake Chat</div>
"""

st.set_page_config(page_title="SQL Snowflake Chat", page_icon="❄️")
st.markdown(gradient_text_html, unsafe_allow_html=True)
st.caption("Talk your way through data")

# --- AI Model Selection ---
model_options = {
    "Gemini Flash 2.0": "Google Gemini",
    "Deepseek R1": "Deepseek R1",
    "GPT-4o": "GPT-4o"
}
selected_model = st.radio(
    "Choose your AI Model:",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=0,
    horizontal=True,
)
st.session_state["model"] = selected_model

# --- Sidebar: Database Connection Option ---
# Default selection: Cloud Snowflake
db_option = st.sidebar.radio(
    "Choose Database Connection",
    ["Cloud Snowflake", "Local PostgreSQL"],
    index=0,
    help="Select 'Cloud Snowflake' to use your Snowflake database or 'Local PostgreSQL' to connect to your local PostgreSQL database."
)

# ----- Cloud Snowflake Branch -----
if db_option == "Cloud Snowflake":
    st.sidebar.markdown(open("ui/sidebar.md").read())
    selected_table = st.sidebar.selectbox("Select a table:", options=list(snow_ddl.ddl_dict.keys()))
    st.sidebar.markdown(f"### DDL for {selected_table} table")
    st.sidebar.code(snow_ddl.ddl_dict[selected_table], language="sql")
    if st.sidebar.button("Reset Chat"):
        for key in list(st.session_state.keys()):
            if key not in ["model", "db", "messages"]:
                st.session_state.pop(key)
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your SQL assistant. Ask me anything about your database."}]
    st.sidebar.markdown(
        "**Note:** Snowflake data retrieval is enabled.",
        unsafe_allow_html=True,
    )
    st.write(open("ui/styles.md").read(), unsafe_allow_html=True)
    try:
        # Build Snowflake connection URI from individual secrets
        account = st.secrets["ACCOUNT"]
        user = st.secrets["USER_NAME"]
        password = st.secrets["PASSWORD"]
        role = st.secrets["ROLE"]
        database = st.secrets["DATABASE"]
        schema = st.secrets["SCHEMA"]
        warehouse = st.secrets["WAREHOUSE"]
        uri = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"
        from langchain_community.utilities import SQLDatabase
        snowflake_db = SQLDatabase.from_uri(uri)
        st.session_state.db = snowflake_db
        if st.session_state["model"] != "Gemini Flash 2.0":
            st.error("please use the Google Gemini model, the selected model has reached the credit limit")
        else:
            st.success("Connected to Shubham's Snowflake Account!")
    except Exception as e:
        st.error(f"Snowflake connection error: {e}")
    
# ----- Local PostgreSQL Branch -----
else:
    st.sidebar.subheader("Local PostgreSQL Settings")
    st.sidebar.write("Connect to your local PostgreSQL database:")
    pg_host = st.sidebar.text_input("Host", value="localhost", key="pg_host")
    pg_port = st.sidebar.text_input("Port", value="5432", key="pg_port")
    pg_user = st.sidebar.text_input("User", value="proxim", key="pg_user")
    pg_database = st.sidebar.text_input("Database", value="store_sales", key="pg_database")
    if st.sidebar.button("Connect to PostgreSQL"):
        try:
            db = pg_init_database(pg_user, pg_host, pg_port, pg_database)
            st.session_state.db = db
            st.success("Connected to PostgreSQL!")
        except Exception as e:
            st.error(f"Connection error: {e}")

# ---------------------------
# Display Chat History (Unified for Both Branches)
# ---------------------------
for msg in st.session_state["messages"]:
    message_func(msg["content"], is_user=(msg["role"]=="user"), model=st.session_state["model"])

# ---------------------------
# Unified Chat Input Widget (Always Visible)
# ---------------------------
user_input = st.chat_input("Type a message...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    if db_option == "Local PostgreSQL":
        if st.session_state.get("db") is None:
            st.error("Not connected to PostgreSQL.")
        else:
            if any(keyword in user_input.lower() for keyword in ["chart", "plot", "visualize", "graph"]):
                df, sql_used = pg_get_visualization_data(user_input, st.session_state.db, st.session_state["messages"])
                if df.empty:
                    response = "No data returned or error occurred."
                else:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(5,5), dpi=100)
                    if "line" in user_input.lower():
                        if df.shape[1] >= 2:
                            ax.plot(df.iloc[:,0], df.iloc[:,1], marker='o')
                            ax.set_xlabel(df.columns[0])
                            ax.set_ylabel(df.columns[1])
                            ax.set_title("Line Chart")
                            pg_adjust_label_fontsize(ax)
                            st.pyplot(fig)
                        else:
                            st.write("Not enough columns for a line chart.")
                    elif "bar" in user_input.lower():
                        if df.shape[1] >= 2:
                            ax.bar(df.iloc[:,0], df.iloc[:,1])
                            ax.set_xlabel(df.columns[0])
                            ax.set_ylabel(df.columns[1])
                            ax.set_title("Bar Chart")
                            pg_adjust_label_fontsize(ax)
                            st.pyplot(fig)
                        else:
                            st.write("Not enough columns for a bar chart.")
                    else:
                        st.dataframe(df)
                    st.markdown("**SQL Query used:** `" + sql_used + "`")
                    response = ""
            else:
                resp, sql_used = pg_get_response_with_sql(user_input, st.session_state.db, st.session_state["messages"])
                resp = pg_strip_code_fences(resp)
                st.markdown(resp)
                st.markdown("**SQL Query used:** `" + sql_used + "`")
                response = resp
            st.session_state["messages"].append({"role": "assistant", "content": response})
    else:
        # Cloud Snowflake Branch
        if st.session_state.get("db") is None:
            st.error("Not connected to Snowflake.")
        else:
            try:
                if any(keyword in user_input.lower() for keyword in ["chart", "plot", "visualize", "graph"]):
                    df, sql_used = sf_get_visualization_data(user_input, st.session_state.db, st.session_state["messages"])
                    if df.empty:
                        response = "No data returned or error occurred."
                    else:
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(figsize=(5,5), dpi=100)
                        if "line" in user_input.lower():
                            if df.shape[1] >= 2:
                                ax.plot(df.iloc[:,0], df.iloc[:,1], marker='o')
                                ax.set_xlabel(df.columns[0])
                                ax.set_ylabel(df.columns[1])
                                ax.set_title("Line Chart")
                                sf_adjust_label_fontsize(ax)
                                st.pyplot(fig)
                            else:
                                st.write("Not enough columns for a line chart.")
                        elif "bar" in user_input.lower():
                            if df.shape[1] >= 2:
                                ax.bar(df.iloc[:,0], df.iloc[:,1])
                                ax.set_xlabel(df.columns[0])
                                ax.set_ylabel(df.columns[1])
                                ax.set_title("Bar Chart")
                                sf_adjust_label_fontsize(ax)
                                st.pyplot(fig)
                            else:
                                st.write("Not enough columns for a bar chart.")
                        else:
                            st.dataframe(df)
                        st.markdown("**SQL Query used:** `" + sql_used + "`")
                        response = ""
                else:
                    resp, sql_used = sf_get_response_with_sql(user_input, st.session_state.db, st.session_state["messages"])
                    resp = sf_strip_code_fences(resp)
                    st.markdown(resp)
                    st.markdown("**SQL Query used:** `" + sql_used + "`")
                    response = resp
                st.session_state["messages"].append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error in Snowflake branch: {e}")
