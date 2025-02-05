# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def query_analyser(state:MyState,testing=False)-> Literal["home", "mobile","None"]:
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
        else:
            query = state['messages'][-1].content

        customer_package = state.get('customer_package', None)
        if customer_package is None:
            state['customer_package'] = 'None'
        if state['customer_package'] == 'None':
            system_prompt =  f"""
                            Analyse if the given query and Determine if the user is intrested in Home Internet or Mobile Internet, if you can't detemine the package type with user query answer -> 'None'. 
                                """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{query}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(IntrestedPackage)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"query":query})
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: {response.package_type}")
            
            if response.package_type in ['home','mobile','None']:
                state = {**state,"customer_package": response.package_type}
                return state
            else:
                raise Exception("Package type not in ['home','mobile']")
        return state
    except Exception as e:
        logging.error(f"[{current_time}] [ERROR] Chat error: {str(e)}", exc_info=True)

