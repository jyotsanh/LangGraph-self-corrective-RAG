
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
from langchain.text_splitter import RecursiveCharacterTextSplitter
# langchain_community
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import PyPDFLoader

# langgraph



#openai
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

# def get_llm(model:str='google',temperature:float=0.4):
#     if model=="google":
#         llm = ChatGoogleGenerativeAI(
#                 model="gemini-1.5-flash",
#                 api_key=os.getenv("GOOGLE_API_KEY"),
#                 temperature=temperature,
#                 max_tokens=None,
#                 timeout=None,
#                 max_retries=2,
#             # other params...
#             )
#         return llm
#     elif model=="openai":
#         llm=ChatOpenAI(
#                 api_key=os.getenv('OPENAI_API_KEY'),
#                 model="gpt-4o-mini", 
#                 temperature=temperature,
               
#             )
        
#         return llm
#     elif model=="groq":
#         llm = ChatGroq(
#                 model="mixtral-8x7b-32768",
#                 api_key=os.getenv("GROQ_API_KEY"),
#                 temperature=temperature,
#                 max_tokens=None,
#                 timeout=None,
#                 max_retries=2,
#                 # other params...
#             )
#     return llm


class LLMFactory:
    def __init__(self, temperature: float = 0.4):
        self.temperature = temperature
        self.llm_registry = {
            "google": self._create_google_llm,
            "openai": self._create_openai_llm,
            "groq": self._create_groq_llm,
            "deepseek": self._create_deepseek_llm,
            # Add more LLMs here...
        }

    def _create_google_llm(self):
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=self.temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def _create_openai_llm(self):
        return ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini",
            temperature=self.temperature,
        )

    def _create_groq_llm(self):
        return ChatGroq(
            model="mixtral-8x7b-32768",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=self.temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

    def _create_deepseek_llm(self):
        #client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
        return ChatOpenAI(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base="https://api.deepseek.com",
        ) 
    
    # Method to get the appropriate LLM
    def get_llm(self, model: str):
        if model not in self.llm_registry:
            raise ValueError(f"Unsupported model '{model}'. Available options are: {list(self.llm_registry.keys())}")
        return self.llm_registry[model]()

def get_llm(model: str, temperature: float = 0.4):
    return LLMFactory(temperature=temperature).get_llm(model)



def _load_pdf(pdf_path: str):
    """Helper function to load documents from a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
    
    loader = PyPDFLoader(pdf_path)
    return loader.load()

def _split_documents(docs_list):
    """Helper function to split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=600, chunk_overlap=100
    )
    return text_splitter.split_documents(docs_list)

def _initialize_vectorstore(doc_splits, embd):
    """Helper function to initialize vector store with embeddings."""
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embd,
    )
    return vectorstore.as_retriever()


def get_embedding(model:str='google'):
    try:
        if model == "google":
            api_key = os.getenv("GOOGLE_API_KEY2")
            if not api_key:
                raise ValueError("Google API key is missing")
            return GoogleGenerativeAIEmbeddings(api_key=api_key)
        
        if model == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key is missing")
            return OpenAIEmbeddings(api_key=api_key)

        raise ValueError(f"Unsupported embedding model: {model}")
    
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(e)
    return None
