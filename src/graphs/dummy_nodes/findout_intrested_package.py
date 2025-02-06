# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging


def findout_intrested_package(state:MyState,testing=False):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
        else:
            query = state['messages'][-1].content

        package_name = state.get('package_name', None) #-> see if the customer package is set or not, if not set the customer package to None

        if package_name is None:
            state['package_name'] = 'None'
        
        if state['package_name'] == 'None' and state['customer_type'] == 'old':
            
            package_dict = state['customer_package']
            customer_package = package_dict['package_type']
            system_prompt =  f"""
                            
                            You are STC assisstant, You know which package does customer has,
                             but still you don't know which package is he intrested in.
                             you need to findout if the user,
                            is intrested in Home Internet or Mobile Internet.
                            response like : "since you are old customer and your current package is {customer_package} package, can i assume you are intrested in {customer_package} package"
                            Ask user very politely.
                            Be very friendly while asking the question.
                            """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{query}"),
                ]
            )
            logging.info(f"Customer is a old customer with package : {customer_package}")
            # LLM with function call
            llm = get_llm(model="google",temperature=0.6)
            # structured_llm_router = llm.with_structured_output(IntrestedPackage)
            chain = route_prompt | llm
            
            response = chain.invoke({"query":query})
            
            state = {**state,"messages": response.content}
            print(state)
            return state
        
        elif state['package_name'] == 'None' and state['customer_type'] == 'new':
            logging.info(f"Customer is a new customer")
            system_prompt =  f"""
                            
                            You are STC assisstant and you need to findout if the user,
                            is intrested in Home Internet or Mobile Internet.
                            Ask user very politely.
                            Be very friendly while asking the question.
                            """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{query}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0.6)
            # structured_llm_router = llm.with_structured_output(IntrestedPackage)
            chain = route_prompt | llm
            
            response = chain.invoke({"query":query})
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: END")
        
            state = {**state,"messages": [*state['messages'],response.content]}
            return state
        return state
    except Exception as e:
        logging.error(f"['fincout_intrested_package'] [ERROR] Chat error: {str(e)}", exc_info=True)

def find_out_package_type(state:MyState,testing=False)->str:
    try:
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
            # conversation_history = "\n".join([msg for msg in state['messages']])
        else:
            query = state["messages"][-1].content
            # conversation_history = "\n".join([msg.content for msg in state['messages']])

        
        system_prompt =  f"""
                       
                        You have to find out , by asking the customer, that if he is intrested in which package type from ['pre-paid','post-paid'], Now the customer has {state['package_name']} internet package.\n
                        In {state['package_name']} internet package
                        there are two kind available:
                            - pre-paid 
                            - post-paid
                        customer can also be intrested in both packages, 
                        so ask properly.

                        """
        route_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{query}"),
            ]
        )
        # LLM with function call
        llm = get_llm(model="google",temperature=0.6)
        
        chain = route_prompt | llm
        
        response = chain.invoke({"query": query})
        # Log routing decision
        logging.info(f"Query: {query} -> Routing to: END")
        
        state = {**state,"messages":[*state['messages'],response.content]}
        return state
    except Exception as e:
        logging.error(f"FILE ['fincout_intrested_package'->find_out_package_type] [ERROR] Chat error: {str(e)}", exc_info=True)