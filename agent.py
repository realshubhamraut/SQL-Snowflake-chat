# agent.py
from dataclasses import dataclass
from typing import Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# Exported items
__all__ = ["MessagesState", "create_agent"]

@dataclass
class MessagesState:
    messages: Annotated[Sequence[BaseMessage], add_messages]

memory = MemorySaver()

# Model configuration for Google Gemini only
@dataclass
class ModelConfig:
    model_name: str
    api_key: str
    base_url: Optional[str] = None

model_configurations = {
    "Google Gemini": ModelConfig(
         model_name="models/gemini-2.0-flash",
         api_key=__import__("streamlit").secrets["GEMINI_API_KEY"],
         base_url=None,
    )
}

sys_msg = SystemMessage(
    content="""You're an AI assistant specializing in data analysis with Snowflake SQL. When providing responses, strive to be friendly and conversational (like a tutor or friend). You have access to the following tools:
    - Database_Schema: Search for database schema details before generating SQL code.
    - Internet_Search: Look up Snowflake SQL–related information when needed.
    """
)

# Tools are imported from tools.py (see that file)
from tools import retriever_tool, search
tools = [retriever_tool, search]

def create_agent(callback_handler) -> StateGraph:
    config = model_configurations["Google Gemini"]
    if not config.api_key:
        raise ValueError("API key for Google Gemini is not set. Please check your secrets configuration.")
    llm = ChatGoogleGenerativeAI(
         model=config.model_name,
         google_api_key=config.api_key,
         callbacks=[callback_handler],
         temperature=0,
         base_url=config.base_url,
         streaming=True,
    )
    llm_with_tools = llm.bind_tools(tools)

    def llm_agent(state: MessagesState):
         return {"messages": [llm_with_tools.invoke([sys_msg] + state.messages)]}

    builder = StateGraph(MessagesState)
    builder.add_node("llm_agent", llm_agent)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "llm_agent")
    builder.add_conditional_edges("llm_agent", tools_condition)
    builder.add_edge("tools", "llm_agent")
    builder.add_edge("llm_agent", END)
    react_graph = builder.compile(checkpointer=memory)
    return react_graph
