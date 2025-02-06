# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def generate_response(state:MyState):
    try:
        pass
    except Exception as e:
        logging.error(f"FILE ['generate_response'->generate_response] [ERROR] Chat error: {str(e)}", exc_info=True)