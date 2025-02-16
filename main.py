import re
import io
import warnings
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# --- Helper Function to Parse Customer Details ---
def parse_customer_details(response_text):
    """
    Parse text output with customer details into a list of dictionaries.
    Expected format per line:
      Name: customer_id <id>, email <email>, phone <phone>, address <address>, total spent $<amount>
    """
    rows = []
    for line in response_text.strip().splitlines():
        if ": " in line:
            name_part, details = line.split(": ", 1)
            name = name_part.strip()
            fields = [field.strip() for field in details.split(",")]
            row = {"Name": name}
            for field in fields:
                if field.startswith("customer_id"):
                    row["Customer_ID"] = field.replace("customer_id", "").strip()
                elif field.startswith("email"):
                    row["Email"] = field.replace("email", "").strip()
                elif field.startswith("phone"):
                    row["Phone"] = field.replace("phone", "").strip()
                elif field.startswith("address"):
                    row["Address"] = field.replace("address", "").strip()
                elif field.startswith("total spent"):
                    row["Total_Spent"] = field.replace("total spent", "").replace("$", "").strip()
            rows.append(row)
    return rows

# --- Initialize Essential Session State Keys ---
if "model" not in st.session_state:
    st.session_state["model"] = "Gemini Flash 2.0"
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your SQL assistant. Ask me anything about your database.", "type": "text"}]
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
    "Gemini Flash 2.0": "Gemini Flash 2.0",
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
    st.sidebar.text('for user reference only (no need for sql-chat)')
    st.sidebar.code(snow_ddl.ddl_dict[selected_table], language="sql")
    if st.sidebar.button("Reset Chat"):
        for key in list(st.session_state.keys()):
            if key not in ["model", "db", "messages"]:
                st.session_state.pop(key)
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your SQL assistant. Ask me anything about your database.", "type": "text"}]
    st.sidebar.markdown("**Note:** Snowflake data retrieval is enabled.", unsafe_allow_html=True)
    st.write(open("ui/styles.md").read(), unsafe_allow_html=True)
    try:
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
        st.session_state["db"] = snowflake_db
        if st.session_state["model"] != "Gemini Flash 2.0":
            st.error("please use the Google Gemini model, the selected model has reached the credit limit")
        else:
            st.success("Connected to Shubham's Snowflake Account!")
    except Exception as e:
        st.error(f"Snowflake connection error: {e}")
    
# ----- Local PostgreSQL Branch -----
else:
    st.sidebar.write("Connect to your local PostgreSQL database:")
    st.sidebar.write("---")
    st.sidebar.write("to use Local PostgreSQL you need to use the local version of this app by cloning repository")
    st.sidebar.subheader("Local PostgreSQL Settings")
    pg_host = st.sidebar.text_input("Host", value="localhost", key="pg_host")
    pg_port = st.sidebar.text_input("Port", value="5432", key="pg_port")
    pg_user = st.sidebar.text_input("User", value="", key="pg_user")
    pg_database = st.sidebar.text_input("Database", value="store_sales", key="pg_database")
    if st.sidebar.button("Connect to PostgreSQL"):
        try:
            db = pg_init_database(pg_user, pg_host, pg_port, pg_database)
            st.session_state["db"] = db
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
    
    def render_chart(df, chart_type, adjust_fn):
        fig, ax = plt.subplots(figsize=(5,5), dpi=100)
        # Set background color for figure and axes
        fig.patch.set_facecolor("#101414")
        ax.set_facecolor("#101414")
        # Set tick label colors to white
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        if chart_type == "line" and df.shape[1] >= 2:
            ax.plot(df.iloc[:,0], df.iloc[:,1], marker='o', color="skyblue")  # skyblue line
            ax.set_xlabel(df.columns[0], color="white")
            ax.set_ylabel(df.columns[1], color="white")
            ax.set_title("Line Chart", color="white")
        elif chart_type == "bar" and df.shape[1] >= 2:
            ax.bar(df.iloc[:,0], df.iloc[:,1], color="skyblue")  # skyblue bars
            ax.set_xlabel(df.columns[0], color="white")
            ax.set_ylabel(df.columns[1], color="white")
            ax.set_title("Bar Chart", color="white")
        elif chart_type == "pie" and df.shape[1] >= 2:
            wedges, texts, autotexts = ax.pie(df.iloc[:,1], labels=df.iloc[:,0], autopct='%1.1f%%', textprops=dict(color="white"))
            ax.set_title("Pie Chart", color="white")
        elif chart_type == "histogram":
            ax.hist(df.iloc[:,1], bins=10, color="skyblue", edgecolor="black")  # skyblue histogram bars
            ax.set_title("Histogram", color="white")
        elif chart_type == "scatter" and df.shape[1] >= 2:
            ax.scatter(df.iloc[:,0], df.iloc[:,1], color="white")
            ax.set_xlabel(df.columns[0], color="white")
            ax.set_ylabel(df.columns[1], color="white")
            ax.set_title("Scatter Plot", color="white")
        elif chart_type == "area" and df.shape[1] >= 2:
            ax.fill_between(range(len(df.iloc[:,1])), df.iloc[:,1], color="white", alpha=0.5)
            ax.set_title("Area Chart", color="white")
        elif chart_type == "bubble" and df.shape[1] >= 2:
            sizes = (df.iloc[:,1] - df.iloc[:,1].min() + 10) * 10
            ax.scatter(df.iloc[:,0], df.iloc[:,1], s=sizes, alpha=0.5, color="white")
            ax.set_xlabel(df.columns[0], color="white")
            ax.set_ylabel(df.columns[1], color="white")
            ax.set_title("Bubble Chart", color="white")
        adjust_fn(ax)
        st.pyplot(fig)
    
    # Determine chart type based on keywords in user_input
    chart_types = ["pie", "histogram", "scatter", "area", "bubble", "line", "bar"]
    selected_chart = None
    for ct in chart_types:
        if ct in user_input.lower():
            selected_chart = ct
            break

    if st.session_state["db"] is None:
        st.error("Not connected to a database.")
    else:
        if selected_chart:
            if db_option == "Local PostgreSQL":
                df, sql_used = pg_get_visualization_data(user_input, st.session_state.db, st.session_state["messages"])
            else:
                df, sql_used = sf_get_visualization_data(user_input, st.session_state.db, st.session_state["messages"])
            if df.empty:
                response = "No data returned or error occurred."
            else:
                render_chart(df, selected_chart, pg_adjust_label_fontsize if db_option == "Local PostgreSQL" else sf_adjust_label_fontsize)
                st.markdown("**SQL Query used:** `" + sql_used + "`")
                response = ""
        else:
            if db_option == "Local PostgreSQL":
                resp, sql_used = pg_get_response_with_sql(user_input, st.session_state.db, st.session_state["messages"])
                resp = pg_strip_code_fences(resp)
            else:
                resp, sql_used = sf_get_response_with_sql(user_input, st.session_state.db, st.session_state["messages"])
                resp = sf_strip_code_fences(resp)
            rows = parse_customer_details(resp)
            if rows:
                st.dataframe(pd.DataFrame(rows))
                response = pd.DataFrame(rows).to_html(index=False)
            else:
                st.markdown(resp)
                response = resp
            st.markdown("**SQL Query used:** `" + sql_used + "`")
        st.session_state["messages"].append({"role": "assistant", "content": response})
