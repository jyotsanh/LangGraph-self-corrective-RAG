from fastapi import APIRouter, Query
from graphs.agent import get_response
from pydantic import BaseModel

router = APIRouter(prefix="/response", tags=["Chat"])

# libs
from libs.libs import *

# logs
import time
from logs.logger_config import logger as logging
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@router.post("/")
def chat_endpoint(query: str, senderId: str):
    """
    Handle chat interactions with the AI assistant.
    
    :param request: Chat request containing query and sender ID
    :return: AI-generated response
    """
    try:
        # Measure the start time 
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"[{timestamp}] [CHAT] Received query from senderId={senderId}: {query}")
        
        # Log function entry
        logging.info(f"[{timestamp}] [CHAT] Entering `get_response` function")
        
        response = get_response(query, senderId)
        if response is None:
            raise Exception("Response from `get_response` function is `None` ")
        response_time = time.time() - start_time  # Calculate response time
        logging.info(f"[{timestamp}] [CHAT] Response generated in {response_time:.2f}s")
        logging.info(f"[{timestamp}] [BOT] Response: {response}")
                
        return {"msg":response}
    
    except Exception as e:
        # Handling the Error 
        logging.error(f"[{timestamp}] [ERROR] Chat error: {str(e)}", exc_info=True)
        return {
                "msg": "I'm sorry, there was an error processing your request."
            }