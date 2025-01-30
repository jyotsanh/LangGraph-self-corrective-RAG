from graphs.graph_builder import build_graph

#libs
from libs.libs import *

#state
from core.state import *

# db
from models.db import *

def update_vector_store(vector_store: VectorDB, sender_id):
    try:
        collection_name=os.getenv("GENERAL_STC")
        print(f"create a vector store for ,{collection_name}")
        embedding_function = get_embedding(model="openai")
        response = VectorStore(
                            collection_name=os.getenv("GENERAL_STC"),
                            store_type=vector_store, 
                            embeddings =embedding_function, 
                            path = "./data/FormattedData/GeneralFAQ.md"
                            ).create_vector_store()
        return response
    except Exception as e:
        return e 

def update_general_faq_stc(vector_store: VectorDB):
    
    """
    Update the general faq collection in vector store using the markdown file at ./data/MarkDownData/GeneralFAQ.md.

    Parameters:
    - vector_store (VectorDB): The type of vector store to update.

    Returns:
    - dict: A dictionary indicating whether the update was successful or not.
    """
    try:
        collection_name=os.getenv("GENERAL_STC")
        print(f"create a vector store for ,{collection_name}")
        embedding_function = get_embedding(model="openai")
        response = VectorStore(
                            collection_name=os.getenv("GENERAL_STC"),
                            store_type=vector_store, 
                            embeddings=embedding_function, 
                            path = "./data/FormattedData/GeneralFAQ.md"
                            ).create_vector_store()
        return response
    except Exception as e:
        return e