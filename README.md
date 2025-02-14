# SQL-Snowflake-chat ❄️ 
#### also with local postgres 🐘



[![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)

[![Gemini](https://img.shields.io/badge/-Gemini-412991?style=flat-square&logo=google-gemini&logoColor=white)](https://gemini.google.com/)

[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)



[![Snowflake](https://img.shields.io/badge/-Snowflake-29BFFF?style=flat-square&logo=snowflake&logoColor=white)](https://www.snowflake.com/en/)


[![Langchain](https://img.shields.io/badge/-Langchain-gray?style=flat-square)](https://www.langchain.com/)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chat-sql-in-natural-language.streamlit.app/)


**SQL-Snowflake-chat** is a user-friendly application that lets you interact with your Snowflake and local PostgreSQL data using natural language queries. Simply type your questions, and SQL-Snowflake-chat will generate the SQL query and return the data you need. It eliminates the need for complex SQL queries and makes data access easy. Enjoy real‑time data retrieval, interactive visualizations, and a sleek dark-themed UI—all through a conversational interface.

## Supported LLM's


- Gemini Flash 2.0
- Deepseek R1
- GPT-4o


## Technology Stack

- **Frontend:**  
  Streamlit with a custom dark theme

- **Data Processing & Visualization:**  
  Pandas, Matplotlib

- **Database Connectivity:**  
  SQLAlchemy, psycopg2-binary, snowflake-connector-python, snowflake-sqlalchemy

- **LLM & Query Generation:**  
  Google Gemini via `langchain_google_genai`



## 🌟 Features

- **Conversational AI**: Use Google Gemini and other models to translate natural language into precise SQL queries.
- **Conversational Memory**: Retains context for interactive, dynamic responses.
- **Snowflake Integration**: Offers seamless, real-time data insights straight from your Snowflake database.
- **Self-healing SQL**: Proactively suggests solutions for SQL errors, streamlining data access.
- **Interactive User Interface**: Transforms data querying into an engaging conversation, complete with a chat reset option.
- **Agent-based Architecture**: Utilizes an agent to manage interactions and tool usage.
- **Plot Charts Automatically, without code** - Want quick insight just ask to plot the required charts/graphs, it will figure out the required query by relating tables in database, I've optimized the code for removing uncecessary data, and will show you just vizualisation.

## 🛠️ Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<your-username>/sql-snowflake-chat.git
   cd sql-snowflake-chat
   ```

2. Install the required packages:
   ```cd SQL-Snowflake-chat```

   ```pip install -r requirements.txt```

   ---


3. Set up your `GEMINI_API`, `ACCOUNT`, `USER_NAME`, `PASSWORD`, `ROLE`, `DATABASE`, `SCHEMA`, `WAREHOUSE`,`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_NAMESPACE_ID`,
   `CLOUDFLARE_API_TOKEN` in project directory `secrets.toml`.
   Cloudflare is used here for caching Snowflake responses in KV.



4. Make your schemas and store them in docs folder that matches your database.

5. Create supabase extention, table and function from the supabase/scripts.sql.

6. Run `python ingest.py` to get convert to embeddings and store as an index file.

7. Run the Streamlit app to start chatting:
   ```streamlit run main.py```

---
## 🤝 Contributing

Feel free to contribute to this project by submitting a pull request or opening an issue. Your feedback and suggestions are greatly appreciated!
