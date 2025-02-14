# ingest.py
from typing import Any, Dict, List
import streamlit as st
from langchain.document_loaders import DirectoryLoader
from langchain_community.embeddings import FakeEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from pydantic import BaseModel

class Config(BaseModel):
    chunk_size: int = 1000
    chunk_overlap: int = 0
    docs_dir: str = "docs/"
    docs_glob: str = "**/*.md"

class DocumentProcessor:
    def __init__(self, config: Config):
        self.loader = DirectoryLoader(config.docs_dir, glob=config.docs_glob)
        self.text_splitter = CharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        self.embeddings = FakeEmbeddings(size=768)
    
    def process(self) -> List[Any]:
        data = self.loader.load()
        texts = self.text_splitter.split_documents(data)
        # Optionally, you can use self.embeddings.embed_documents(texts) to embed them.
        return texts

def run() -> List[Any]:
    config = Config()
    doc_processor = DocumentProcessor(config)
    result = doc_processor.process()
    return result

if __name__ == "__main__":
    run()
