# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def mobile_internet(state:MyState,testing=False)-> Literal["prepaid", "postpaid","all","unclear"]:
    try:
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
            conversation_history = "\n".join([msg for msg in state['messages']])
        else:
            query = state["messages"][-1].content
            conversation_history = "\n".join([msg.content for msg in state['messages']])

            
        if state['package_name'] == 'mobile':
            system_prompt =  f"""
                            You know that Customer is Intrested in {state['package_name']} package.
                            Analyse the given conversation history and Determine if the user is intrested in prepaid or postpaid package type of {state['package_name']} package \n
                            if the user wants to know both package type then answer -> all \n
                            if you can't detemine the package type with conversation history then answer -> 'None'. 

                                """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{conversation_history}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(IntrestedPackageType)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"conversation_history": conversation_history})
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: {response.package_type}")
            
            if response.package_type in ["prepaid", "postpaid","all","unclear"]:
                state = {**state,"package_type": response.package_type}
                return state
            else:
                raise Exception("Package type not in ['prepaid','postpaid','all','unclear']")
        else:
            raise Exception("Package name is not mobile, It was supposed to be mobile.")
    except Exception as e:
        logging.error(f"FILE ['mobile_internet'->mobile_internet] [ERROR] Chat error: {str(e)}", exc_info=True)