from fastapi import APIRouter, Query
from graphs.agent import get_response
from pydantic import BaseModel

router = APIRouter(prefix="/response", tags=["Chat"])

# libs
from libs.libs import *

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
def chat_endpoint(query: str, senderId: str):
    """
    Handle chat interactions with the AI assistant.
    
    :param request: Chat request containing query and sender ID
    :return: AI-generated response
    """
    try:
        print("---------------------------------------------------------------------------Getting response from Runnable LLM node---------------------------------------------------------------------------")
        
        # Measure the start time 
        start_time = time.time()
        
        response = get_response(query, senderId)
        
        # Measure the end time
        end_time = time.time()
        # Calculate the time taken
        response_time = end_time - start_time
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log user query
        user_log_message = f"{current_time}\nUser Query: {query}\n"
        logging.info(user_log_message)

        # Log bot response with response time
        bot_log_message = (
            f"{current_time}\nBot Response: {response['messages'][-1].content}\n"
            f"Time Taken: {response_time:.2f} seconds\n"
            "----------------------------------------------------------------------------------------------------------------------------"
        )
        logging.info(bot_log_message)
        print()
        print("|---------------------------------------------------------Bot  Response--------------------------------------------------------------|")
        print("Response: \n",response['messages'][-1].content)
        print("|---------------------------------------------------------API  Response--------------------------------------------------------------|")
        print()
        # return ChatResponse(message=response['messages'][-1].content)
        respond = {"msg":response['messages'][-1].content}
        
        print("------------------------------------------------------------------------------Getting response from Runnable LLM node-------------------------------------------------------------------------------")
        return respond
    except Exception as e:
        # Log the error (you'd use proper logging in production)
        print(f"Chat error: {e}")
        respond = {
            "msg": "I'm sorry, there was an error processing your request."
        }
        return respond