# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def home_internet(state:MyState,testing=False)-> Literal["home", "mobile","None"]:
    try:
        pass
    except Exception as e:
        logging.error(f"FILE ['home_internet'->home_internet] [ERROR] Chat error: {str(e)}", exc_info=True)


def all_home_packages(state:MyState,testing=False)-> Literal["home", "mobile","None"]:
    try:
        pass
    except Exception as e:
        logging.error(f"FILE ['home_internet'->all_home_packages] [ERROR] Chat error: {str(e)}", exc_info=True)