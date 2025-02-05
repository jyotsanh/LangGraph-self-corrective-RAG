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
        if state['package_name'] == 'None':
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
            llm = get_llm(model="google",temperature=0)
            # structured_llm_router = llm.with_structured_output(IntrestedPackage)
            chain = route_prompt | llm
            
            response = chain.invoke({"query":query})
            
            state = {**state,"messages": response.content}
            return state
        return state
    except Exception as e:
        logging.error(f"[{current_time}] [ERROR] Chat error: {str(e)}", exc_info=True)