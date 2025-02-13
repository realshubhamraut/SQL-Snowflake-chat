# SQL-Snowflake-chat 💬❄️

[![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/-OpenAI-412991?style=flat-square&logo=openai&logoColor=white)](https://openai.com/)
[![Snowflake](https://img.shields.io/badge/-Snowflake-29BFFF?style=flat-square&logo=snowflake&logoColor=white)](https://www.snowflake.com/en/)
[![Supabase](https://img.shields.io/badge/-Supabase-00C04A?style=flat-square&logo=supabase&logoColor=white)](https://www.supabase.io/)
[![AWS](https://img.shields.io/badge/-AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Langchain](https://img.shields.io/badge/-Langchain-gray?style=flat-square)](https://www.langchain.com/)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://SQL-Snowflake-chat.streamlit.app/)


**SQL-Snowflake-chat** is a user-friendly application that lets you interact with your Snowflake data using natural language queries. Simply type your questions, and SQL-Snowflake-chat will generate the SQL query and return the data you need. It eliminates the need for complex SQL queries and makes data access easy. SQL-Snowflake-chat helps you make data-driven decisions quickly and efficiently by simplifying the process of getting insights from your data.

## Supported LLM's

- Deepseek R1
- GPT-4o
- Qwen 2.5
- Gemini Flash 1.5 8B
- Claude 3 Haiku
- Llama 3.2 3B
- Llama 3.1 405B


## 🌟 Features

- **Conversational AI**: Use ChatGPT and other models to translate natural language into precise SQL queries.
- **Conversational Memory**: Retains context for interactive, dynamic responses.
- **Snowflake Integration**: Offers seamless, real-time data insights straight from your Snowflake database.
- **Self-healing SQL**: Proactively suggests solutions for SQL errors, streamlining data access.
- **Interactive User Interface**: Transforms data querying into an engaging conversation, complete with a chat reset option.
- **Agent-based Architecture**: Utilizes an agent to manage interactions and tool usage.

## 🛠️ Installation

1. Clone this repository:
   git clone https://github.com/realshubhamraut/SQL-Snowflake-chat.git

2. Install the required packages:
   cd SQL-Snowflake-chat
   pip install -r requirements.txt

3. Set up your `OPENAI_API_KEY`, `ACCOUNT`, `USER_NAME`, `PASSWORD`, `ROLE`, `DATABASE`, `SCHEMA`, `WAREHOUSE`, `SUPABASE_URL` , `SUPABASE_SERVICE_KEY`, `SUPABASE_STORAGE_URL`,`CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_NAMESPACE_ID`,
   `CLOUDFLARE_API_TOKEN` in project directory `secrets.toml`.
   Cloudflare is used here for caching Snowflake responses in KV.

4. Make your schemas and store them in docs folder that matches your database.

5. Create supabase extention, table and function from the supabase/scripts.sql.

6. Run `python ingest.py` to get convert to embeddings and store as an index file.

7. Run the Streamlit app to start chatting:
   streamlit run main.py


## 🤝 Contributing

Feel free to contribute to this project by submitting a pull request or opening an issue. Your feedback and suggestions are greatly appreciated!

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://choosealicense.com/licenses/mit/) file for details.
