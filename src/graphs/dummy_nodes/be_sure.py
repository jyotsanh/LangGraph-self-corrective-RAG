# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging



def make_sure_package(state:MyState,testing=False)->Literal["clear","unclear"]:
    try:
        intrested = state.get("intrested_package",None)
        if intrested is None:
            state['intrested_package'] = 'unclear'
        if state['intrested_package'] == 'unclear':
            if testing:
                query = state['messages'][-1]
                conversation_history = "\n".join([msg for msg in state['messages']])
            else:
                query = state["messages"][-1].content
                conversation_history = "\n".join([msg.content for msg in state['messages']])
            customer_package = state['customer_package']
            package_type = customer_package['package_type']
            logging.info(f"Customer Current Package : {package_type}")
            system_prompt =  f"""
                            Analyse the conversation history of customer and findout if customer has said anything about that if he is intrested in home internet or mobile internet.\n
                            

                            if customer has said anything about being intrested in home internet or mobile internet, return -> "clear"
                            otherwise return -> "unclear"
                                """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{conversation_history}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(BeSure)
            chain = route_prompt | structured_llm_router

            response = chain.invoke({"conversation_history": conversation_history})
            

            if response.intrested_package in ['clear','unclear']:
                # Log routing decision
                logging.info(f"User Intrest: {response.intrested_package}")
                state = {**state,"intrested_package": response.intrested_package}
                return state
        else:
            # Do not go to find_intrested_package node to if, if customer is clear, on which package he is intrested in.
            return state
    except Exception as e:
        logging.error(f"FILE[`make_sure_package`] -> Error: {str(e)},")