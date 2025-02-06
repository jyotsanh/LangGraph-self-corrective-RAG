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
            conversation_history = "\n".join([msg for msg in state['messages']])
        else:
            query = state["messages"][-1].content
            conversation_history = "\n".join([msg.content for msg in state['messages']])

        print(f"\n Conversation history: \n{conversation_history} \n")
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
                    ("human", "{conversation_history}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(IntrestedPackage)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"conversation_history": conversation_history})
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: {response.package_name}")
            
            if response.package_name in ['home','mobile','None']:
                state = {**state,"package_name": response.package_name}
                return state
            else:
                raise Exception("Package type not in ['home','mobile']")
        else:

            if testing:
                query = state['messages'][-1]
                conversation_history = "\n".join([msg for msg in state['messages']])
            else:
                query = state["messages"][-1].content
                conversation_history = "\n".join([msg.content for msg in state['messages']])

            package_type = customer_package['package_type']
            logging.info(f"Customer Current Package : {package_type}")
            system_prompt =  f"""
                            Customer Current Package : {package_type}
                            response like : "I see your current package is {package_type}, so can i assume that you are intrested in {package_type}"\n

                            customer can only be intrested in two kind of package 
                            1- Home Internet-> home
                            2- Mobile Internet-> mobile
                            If you can't determine which package user is intrested in with user query answer -> 'None'.\n

                                """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{conversation_history}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(IntrestedPackage)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"conversation_history": conversation_history})
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: {response.package_name}")
            
            if response.package_name in ['home','mobile','None']:
                state = {**state,"package_name": response.package_name}
                return state
        return state
    except Exception as e:
        logging.error(f"FILE['quert analyser'] [ERROR] Chat error: {str(e)}", exc_info=True)

