#libs
from libs.libs import *

#state
from core.state import *

# db
from models.db import *


# logs
import time
from logs.logger_config import logger as logging



async def general_update_function(vector_store, senderId, collection_name):

    logging.info(f"[UPDATE] generalFAQ")


    try:
        collection_name=os.getenv("GeneralFAQ_STC")
        logging.info(f"[UPDATE] create a vector store for -> {collection_name}")
        embedding_function = get_embedding(model="openai")
        await  VectorStore(
                            collection_name = collection_name,
                            store_type=vector_store, 
                            embeddings=embedding_function, 
                            path = "./data/MarkDownData/generalFAQ.md"
                            ).create_vector_store()
        res_message = f"collection name : generalFAQ is updated"

        return res_message
    except Exception as e:
        return e
    

async def home_internet_update_function(vector_store, senderId, collection_name):
    logging.info(f"[UPDATE] home internet")


    try:
        collection_name=os.getenv("Home_Internet_STC")
        logging.info(f"[UPDATE] create a vector store for -> {collection_name}")
        embedding_function = get_embedding(model="openai")
        await VectorStore(
                            collection_name= collection_name,
                            store_type=vector_store, 
                            embeddings=embedding_function, 
                            path = "./data/MarkDownData/HomeInternet.md"
                            ).create_vector_store()
        res_message = f"collection name :home internet is updated"

        return res_message

    except Exception as e:
        return e

    
async def mobile_internet_update_function(vector_store, senderId, collection_name):
    logging.info(f"[UPDATE] mobile internet")

    try:
        collection_name=os.getenv("Mobile_Internet_STC")
        logging.info(f" [UPDATE] create a vector store for -> {collection_name}")
        embedding_function = get_embedding(model="openai")
        await VectorStore(
                            collection_name= collection_name,
                            store_type=vector_store, 
                            embeddings=embedding_function, 
                            path = "./data/MarkDownData/MobileInternet.md"
                            ).create_vector_store()
        res_message = f"collection name : mobile internet is updated"
        return res_message
    except Exception as e:
        return e



