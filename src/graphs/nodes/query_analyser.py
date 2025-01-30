# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

def query_analyser(state:MyState,testing=False) -> Literal["vectorstore", "web_search","greet"]:
    """
    Analyzes a user query and routes it to the appropriate datasource.

    Depending on the content of the query, this function determines whether to 
    route the query to a vectorstore, web search, or simply return a greeting. 
    The vectorstore is used for queries related to specific topics, while the 
    web search is used for general knowledge queries. If the query is a simple 
    greeting, it returns 'greet'.

    Args:
        state (MyState): The current application state containing messages.
        testing (bool, optional): Flag to indicate if testing mode is enabled. 
                                  Defaults to False.

    Returns:
        Literal["vectorstore", "web_search", "greet"]: The determined routing 
        decision for the query.

    Raises:
        ValueError: If the state is invalid or 'messages' are missing or empty.
    """
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
        else:
            query = state['messages'][-1].content
        
        system_prompt =  """
                        You are an expert at routing a user question to a vectorstore,web search and greet.\n
                        The vectorstore contains documents related to the following topics.\n
                        - Who created This Project\n
                        - Who is Jyotsan, His CV details.\n
                        - Game of Thrones\n
                        - The Lord of the Rings\n
                        - Star Wars\n
                        Use the vectorstore for questions on these topics. \n
                        Otherwise, use web-search for General Knowledge type of questions\n.
                        if the query is simple greet then just return greet.\n
                            """
        route_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{query}"),
            ]
        )
            
        # LLM with function call
        llm = get_llm(model="google",temperature=0)
        structured_llm_router = llm.with_structured_output(RouteQuery)
        chain = route_prompt | structured_llm_router
        
        response = chain.invoke({"query":query})
        
        # Log routing decision
        logging.info(f"Query: {query} -> Routing to: {response.datasource}")
        
        return response.datasource
    except Exception as e:
        logging.error(f"[{current_time}] [ERROR] Chat error: {str(e)}", exc_info=True)