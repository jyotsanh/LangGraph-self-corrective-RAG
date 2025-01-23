
from pydantic import BaseModel, Field
import json

# state.py
from typing import Annotated, List, Literal
from langgraph.graph.message import AnyMessage, add_messages
from typing_extensions import TypedDict



from datetime import datetime
import os

# langhcain
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveJsonSplitter
from langchain.schema import Document
from langchain_community.document_loaders.csv_loader import CSVLoader

from langchain_chroma import Chroma
from langchain_milvus import Milvus

# langchain_community
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader


# langgraph



from dotenv import load_dotenv
load_dotenv()

def get_llm(model:str='google',temperature:float=0.4):
    if model=="google":
        llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
            # other params...
            )
        return llm
    elif model=="openai":
        llm=ChatOpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                model="gpt-4o-2024-05-13", 
                temperature=temperature,
                stream_usage=True
            )
        
        return llm
    elif model=="groq":
        llm = ChatGroq(
                model="mixtral-8x7b-32768",
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # other params...
            )
    return llm


def get_embedding(model:str='google'):
    if model=="google":
        embeddings = GoogleGenerativeAIEmbeddings(api_key=os.getenv("GOOGLE_API_KEY"))
        return embeddings