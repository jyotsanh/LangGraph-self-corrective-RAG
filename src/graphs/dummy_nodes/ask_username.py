# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

from langchain.tools import tool

def fetch_customer_package(state: MyState):
    try:

        username = state['customer_name']

        username_list = ['username1','username2','username3','username4']
        if username in username_list:
            data_dict = {
                "package_type":"mobile internet",
                "speed":"500 MBbps",
                "price":"10,000"
            }

            state = {**state,"customer_package":data_dict}
            print(state)
            return state
        else:
            return "This username doesn't exist, please check your username"
    except Exception as e:
        logging.error(f"FILE ['ask_username'->fetch_customer_package] [ERROR] Chat error: {str(e)}", exc_info=True)

from langchain.schema import AIMessage  # Import AIMessage
def ask_customer_username(state:MyState,testing=False):

    try:

        customer_name = state.get("customer_name",None)
        if customer_name is None:
            state['customer_name'] = 'None'

        if state['customer_name'] == 'None':
            message = "please provide your username"
            state = {**state,"messages":[*state['messages'],AIMessage(content=message)]}
            return state
    except Exception as e:
        logging.error(f"FILE ['ask_username'->ask_customer_username] [ERROR] Chat error: {str(e)}", exc_info=True)


def has_username(state:MyState,testing=False)-> Union[Literal["ask_username"], str]:

    try:
        
        customer_name = state.get("customer_name",None)
        if customer_name is None:
            state['customer_name'] = 'None'

        if state['customer_name'] == 'None':
            conversation_history = "\n".join([msg.content for msg in state['messages']])
            system_prompt ="""
                        With given message history analyse if user has given his username or not, \n
                        if conversation history doesn't have username,
                        then simply return `ask_username` \n
                        if conversation history have username,
                        then simply return customer username from conversation history\n
                            """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{conversation_history}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(HasUsername)
            chain = route_prompt | structured_llm_router

            response = chain.invoke({"conversation_history":conversation_history})
            logging.info(f"Routing to: {response.username}")
            if response.username == "ask_username":
                state = {**state,"go_to":"ask_username"}
                return state
            else:
                state['customer_name'] = response.username
                state = {**state,"go_to":"fetch_customer_package"}
                return state
        else:
            # we know the username and shoudl go to fetch_customer_package
            logging.info(f"Customer username: {state['customer_name']}")
            state = {**state,"go_to":"fetch_customer_package"}
            return state


    except Exception as e:
        logging.error(f"FILE ['ask_username'-> has_username] [ERROR] Chat error: {str(e)}", exc_info=True)
