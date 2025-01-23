from fastapi import APIRouter, Query
from graphs.vector_updates import update_vector_store
from pydantic import BaseModel

router = APIRouter(prefix="/update_vectore_store", tags=["Update"])

# libs
from libs.libs import *

#states
from core.state import *

# logging
import logging
import time

# Configure logging
logging.basicConfig(
    filename='logs/history.log',
    level=logging.INFO,
    format='%(message)s'  # Simple format to match your desired output
)
@router.post("/")
def update_endpoint(vectore_store:VectorDB, senderId: str):
    
    try:
        print("---------------------------------------------------------------------------Getting response from Runnable LLM node---------------------------------------------------------------------------")
        
        # Measure the start time 
        start_time = time.time()
        
        response = update_vector_store(vectore_store, senderId)
        
        # Measure the end time
        end_time = time.time()
        # Calculate the time taken
        response_time = end_time - start_time
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log user query
        user_log_message = f"Vector Store: {vectore_store} Updated!!\n Time taken : {response_time}\n" 
        logging.info(user_log_message)
        
        res = {"msg": f"{response}"}
        return res
    except Exception as e:
        # Log the error (you'd use proper logging in production)
        print(f"Chat error: {e}")
        respond = {
            "msg": "I'm sorry, there was an error processing your request."
        }
        return respond