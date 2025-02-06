# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

from langchain.tools import tool

def pre_paid_internet(state: MyState):
    try:

        pass
        
    except Exception as e:
        logging.error(f"FILE ['package_type'->pre_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)

def post_paid_internet(state: MyState):
    try:
        pass
    except Exception as e:
        logging.error(f"FILE ['package_type'->post_paid_internet] [ERROR] Chat error: {str(e)}", exc_info=True)