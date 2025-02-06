# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def collection_info(state:MyState,testing=False) -> Literal["old","new","None"]:
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
        else:
            query = state['messages'][-1].content
        customer_type = state.get('customer_type', None)
        if customer_type is None:
            state['customer_type'] = 'None'
        if state['customer_type'] == 'None':

            system_prompt =  """
                            You are a assisstant at The Saudi Telecom Company (shortened to stc; Arabic: شركة الاتصالات السعودية), trading as STC Group provides ICT services in the Kingdom of Saudi Arabia, across the Middle East and Europe.[3] The group offers landline and fixed infrastructure, mobile and data services, and broadband & cloud computing services. It also offers online payments, telecommunications, IOT, 5G, e-gaming, cybersecurity, digital entertainment, and fintech. 

                            Your task is to Determine if customer is new or existing. 
                            If you can't determine the customer type with user query answer 'None'.
                            """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{query}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(CollectInfo)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"query":query})
            # if response.customer_type == 'None':
            #     return "Are you a Old customer or new customer ?"
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: {response.customer_type}")
            
            if response.customer_type in ['old','new','None']:
                # if response.customer_type == 'new':
                #     pass
                state = {**state,"customer_type": response.customer_type}
                return state
            else:
                raise Exception(f"Invalid customer type by Agent: {response.customer_type}")
        else:
            # This else block is for In case customer_type is changed in-between chat.

            conversation_history = "\n".join([msg.content for msg in state['messages']])
            # print(f"conversation history\n:{conversation_history}\n")
            system_prompt =  """
                            Analyse the all conversation history of user and bot and Determine if the user is new or old customer, \n
                            Things you should consider:\n
                                - User may say "i am new customer" in first message\n, give more priority to recent messages, because , in between chat user may change his mind and say "i am old customer"\n
                            """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{conversation_history}"),
                ]
            )

            

            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(CollectInfo)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"conversation_history":conversation_history})
            logging.info(f"Query: {query} -> Routing to: {response.customer_type}")

            if response.customer_type in ['old','new']:
                state = {**state,"customer_type": response.customer_type}
                return state
            else:
                print("here")
                return state
    except Exception as e:
        logging.error(f"[{current_time}] [ERROR] Chat error: {str(e)}", exc_info=True)

from langchain.schema import AIMessage  # Import AIMessage

def ask_node(state:MyState,testing=False):
    state = {**state,"messages": [*state["messages"], AIMessage(content="Are you an old or new customer?")]}
    return state
