# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

from langchain.schema import AIMessage  # Import AIMessage


def similarity_search(query):
    message = f"similary docs returnedd..."
    return message

# def pre_paid_internet(state: MyState):
#     try:

#         message = f"so you are intrested in {state['package_name']}, pre-paid internet package"
#         state = {**state,"messages":[*state['messages'],AIMessage(content=message)]}

#         logging.info(f"{state['package_name']} pre-paid package -> check relevance")

#         return state
        
#     except Exception as e:
#         logging.error(f"FILE ['package_type'->pre_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)

def pre_paid_internet(state: MyState):
    try:

        packge_name = state['package_name'] # -> home or mobile
        package_type = state['package_type'] # -> post-paid or pre-paid

        query = f"provide all the package details about {packge_name} internet package, package type is {package_type}"

        logging.info(f"sending a similarity serach query for package name: {state['package_name']}, type: {state['package_type']}")
        similar_docs = similarity_search(query=query)

        logging.info(f"{state['package_name']} both package, fetched docs and going to -> check relevance")
        state = {**state,"documents": similar_docs}
        return state
        
    except Exception as e:
        logging.error(f"FILE ['package_type'->pre_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)



# def post_paid_internet(state: MyState)->str:
#     try:
#         message = f"so you are intrested in {state['package_name']}, post-paid internet package"
#         state = {**state,"messages":[*state['messages'],AIMessage(content=message)]}
#         logging.info(f"{state['package_name']} post-paid package -> check relevance")

#         return state
#     except Exception as e:
#         logging.error(f"FILE ['package_type'->post_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)



def post_paid_internet(state: MyState)->str:
    try:
        packge_name = state['package_name'] # -> home or mobile
        package_type = state['package_type'] # -> post-paid or pre-paid

        query = f"provide all the package details about {packge_name} internet package, package type is {package_type}"

        logging.info(f"sending a similarity serach query for package name: {state['package_name']}, type: {state['package_type']}")
        similar_docs = similarity_search(query=query)
        
        logging.info(f"{state['package_name']} both package, fetched docs and going to -> check relevance")
        state = {**state,"documents": similar_docs}
        return state
    except Exception as e:
        logging.error(f"FILE ['package_type'->post_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)