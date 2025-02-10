# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging
from langchain.schema import AIMessage,HumanMessage
def generate_response(state:MyState,testing=False):
    try:
        if state["package_name"] in ['home','mobile']:

            if state.get('documents',None) == None:
                message = f"This is the generative response from llm, {state['package_name']} -> {state['package_type']} "
                state = {**state,"messages":[*state['messages'],HumanMessage(content=message)]}
                logging.info(f"going to -> END")
                return state
            else:
                if testing:
                    query = state['messages'][-1]
                else:
                    query = state['messages'][-1].content
                context = state['documents']

                system_prompt =  """
                            
                            You are STC assisstant,Given the context and user query , provide a short and simple explanation \n
                            Be very friendly while asking the question.\n
                            Use this Context below to answer:\n
                            {context}\n
                            """
                
                query = f"Explain me about {state['package_name']} internte package, \n i am intrested in know about the {state['package_type']} kind of package , pls explain me in short and simple way"
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
                
                response = chain.invoke({"query":query,"context":context})
                if response.content:
                    state = {**state,"messages":[*state['messages'],response.content]}
                else:
                    raise Exception("wrong in response.content")
                return state
    except Exception as e:
        logging.error(f"FILE ['generate_response'->generate_response] [ERROR] Chat error: {str(e)}", exc_info=True)