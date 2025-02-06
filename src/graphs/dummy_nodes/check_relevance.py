# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging


def check_relevance(state: MyState):
    try:
        pass
    except Exception as e:
        logging.error(f"FILE ['check_recheck_relevancelevance'->check_relevance] [ERROR] Chat error: {str(e)}", exc_info=True)