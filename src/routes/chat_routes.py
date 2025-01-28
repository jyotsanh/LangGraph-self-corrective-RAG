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
        print("---------------------------------------------------------------------------Getting response from Runnable LLM node---------------------------------------------------------------------------")
        
        # Measure the start time 
        start_time = time.time()
        logging.info(
            "\n-------------------------------------------------------------------"
            f"\nEntering the `get_response` function at {current_time} seconds\n"
            )
        response = get_response(query, senderId)
        
        # Measure the end time
        end_time = time.time()
        # Calculate the time taken
        response_time = end_time - start_time
        
        
        
        # Log user query
        user_log_message = f"\n{current_time}\nUser Query: {query}\n"
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
        
        logging.info(
            "Sucessfully responded"
            "-------------------------------------------------------------------"
            )
        return respond
    except Exception as e:
        # Log the error (you'd use proper logging in production)
        print(f"Chat error: {e}")
        respond = {
            "msg": "I'm sorry, there was an error processing your request."
        }
        logging.info(
            f"\nChat error: \n{e}\n"
            "-------------------------------------------------------------------"
            )
        return respond