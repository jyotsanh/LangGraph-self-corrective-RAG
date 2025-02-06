# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging
from langchain.schema import AIMessage,HumanMessage
def generate_response(state:MyState):
    try:
        if state["package_name"] in ['home','mobile']:

            
            message = f"This is the generative response from llm, {state['package_name']} -> {state['package_type']} "
            state = {**state,"messages":[*state['messages'],HumanMessage(content=message)]}
            logging.info(f"going to -> END")
            return state
    except Exception as e:
        logging.error(f"FILE ['generate_response'->generate_response] [ERROR] Chat error: {str(e)}", exc_info=True)