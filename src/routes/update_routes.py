from fastapi import APIRouter, Query
from graphs.vector_updates import update_vector_store
from pydantic import BaseModel

router = APIRouter(prefix="/update_vectore_store", tags=["Update"])

# libs
from libs.libs import *

#states
from core.state import *

# logs
import time
from logs.logger_config import logger as logging



@router.post("/")
def update_endpoint(vectore_store:VectorDB, senderId: str):
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"[{timestamp}] [UPDATE] Received request to update vector store for sender ID: {senderId}")
        # Measure the start time 
        start_time = time.time()
        
        response = update_vector_store(vectore_store, senderId)
        
        # Measure the end time
        end_time = time.time()
        # Calculate the time taken
        response_time = end_time - start_time
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log successful update
        logging.info(
            f"[{timestamp}] [UPDATE SUCCESS] Vector store updated successfully!\n"
            f"Sender ID: {senderId}\n"
            f"Vector Store: {vectore_store}\n"
            f"Time Taken: {response_time:.2f} seconds\n"
            "----------------------------------------------------------------------------------------------------------------------------"
        )
        
        res = {"msg": f"{response}"}
        return res
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{timestamp}] [UPDATE ERROR] Failed to update vector store for sender ID: {senderId}\nError: {e}"
        logging.error(error_message)
        respond = {
            "msg": "I'm sorry, there was an error processing your request. Pls check the logs for more details."
        }
        return respond