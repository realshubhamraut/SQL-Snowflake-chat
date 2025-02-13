# chain.py
from dataclasses import dataclass, field
from operator import itemgetter
from typing import Any, Callable, Dict, Optional
import streamlit as st
from langchain_community.embeddings import FakeEmbeddings
from langchain.prompts.prompt import PromptTemplate
from langchain.schema import format_document
from langchain.vectorstores import SupabaseVectorStore
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from supabase.client import Client, create_client
from template import CONDENSE_QUESTION_PROMPT, QA_PROMPT

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
client: Client = create_client(supabase_url, supabase_key)

@dataclass
class ModelConfig:
    model_type: str
    secrets: Dict[str, Any]
    callback_handler: Optional[Callable] = field(default=None)

class ModelWrapper:
    def __init__(self, config: ModelConfig):
        self.model_type = config.model_type
        self.secrets = config.secrets
        self.callback_handler = config.callback_handler
        self.llm = self._setup_llm()

    def _setup_llm(self):
        return ChatGoogleGenerativeAI(
            model="models/gemini-2.0-flash",
            google_api_key=self.secrets["GEMINI_API_KEY"],
            temperature=0.1,
            callbacks=[self.callback_handler],
            max_tokens=700,
            streaming=True,
        )

    def get_chain(self, vectorstore):
        def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
            doc_strings = [format_document(doc, document_prompt) for doc in docs]
            return document_separator.join(doc_strings)

        _inputs = RunnableParallel(
            standalone_question=RunnablePassthrough.assign(
                chat_history=lambda x: get_buffer_string(x["chat_history"])
            )
            | CONDENSE_QUESTION_PROMPT
            | StrOutputParser()
        )
        _context = {
            "context": itemgetter("standalone_question")
            | vectorstore.as_retriever()
            | _combine_documents,
            "question": lambda x: x["standalone_question"],
        }
        conversational_qa_chain = _inputs | _context | QA_PROMPT | self.llm
        return conversational_qa_chain

def load_chain(model_name="google_gemini", callback_handler=None):
    embeddings = FakeEmbeddings(size=768)
    vectorstore = SupabaseVectorStore(
        embedding=embeddings,
        client=client,
        table_name="documents",
        query_name="v_match_documents",
    )
    # Override the retriever with a dummy retriever to disable document retrieval.
    class DummyRetriever:
        def get_relevant_documents(self, query):
            return []
    vectorstore.as_retriever = lambda: DummyRetriever()
    
    model_type = "google_gemini"
    config = ModelConfig(
        model_type=model_type, secrets=st.secrets, callback_handler=callback_handler
    )
    model = ModelWrapper(config)
    return model.get_chain(vectorstore)
