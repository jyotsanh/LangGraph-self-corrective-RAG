# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def mobile_internet(state:MyState,testing=False)-> Literal["home", "mobile","None"]:
    try:
        pass
    except Exception as e:
        logging.error(f"FILE ['mobile_internet'->mobile_internet] [ERROR] Chat error: {str(e)}", exc_info=True)