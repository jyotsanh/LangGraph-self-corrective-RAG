# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

from langchain.schema import AIMessage  # Import AIMessage

#db
from models.db import *

def similarity_search(query):
    message = f"similary docs returnedd..."
    return message

def similarity_search_func(query,package_name):
    if package_name == 'home':
        
        collection_name=os.getenv("Home_Internet_STC")
    elif package_name == 'mobile':
        collection_name = os.getenv("Mobile_Internet_STC")

    logging.info(f"[DOC] Collection name : {collection_name} of {package_name} internet")
    open_embeddings = get_embedding("openai")
    vector_store = VectorStore(
                                    collection_name=collection_name, 
                                    store_type="milvus", 
                                    embeddings =open_embeddings
                                    ).get_vector_store()
    docs = vector_store.similarity_search(query=query,k=3)
    return docs

def pre_paid_internet(state: MyState):
    try:

        package_name = state['package_name'] # -> home or mobile
        package_type = state['package_type'] # -> post-paid or pre-paid

        query = f"provide all the package details about {package_name} internet package, package type is {package_type}"

        logging.info(f"sending a similarity serach query for package name: {state['package_name']}, type: {state['package_type']}")

        similar_docs = similarity_search_func(query,package_name)

        logging.info(f"{state['package_name']} internet ,{package_type} package, fetched docs and going to -> check relevance")
        state = {**state,"documents": similar_docs}
        return state
        
    except Exception as e:
        logging.error(f"FILE ['package_type'->pre_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)


def post_paid_internet(state: MyState)->str:
    try:
        package_name = state['package_name'] # -> home or mobile
        package_type = state['package_type'] # -> post-paid or pre-paid

        query = f"provide all the package details about {package_name} internet package, package type is {package_type}"

        logging.info(f"sending a similarity serach query for package name: {state['package_name']}, type: {state['package_type']}")
        similar_docs = similarity_search_func(query,package_name)

        
        logging.info(f"{state['package_name']} internet ,{package_type} package, fetched docs and going to -> check relevance")
        state = {**state,"documents": similar_docs}
        return state
    except Exception as e:
        logging.error(f"FILE ['package_type'->post_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)