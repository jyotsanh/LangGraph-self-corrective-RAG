# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

from langchain.schema import AIMessage,HumanMessage
def check_relevance(state: MyState):
    try:
        
        message = f"This is the generative response from llm "
        state = {**state,"messages":[*state['messages'],HumanMessage(content=message)]}
        logging.info(f"going to -> generative_response")
        return state
    except Exception as e:
        logging.error(f"FILE ['check_recheck_relevancelevance'->check_relevance] [ERROR] Chat error: {str(e)}", exc_info=True)