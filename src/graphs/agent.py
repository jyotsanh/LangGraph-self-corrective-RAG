from graphs.graph_builder import build_graph

#libs
from libs.libs import *

#state
from core.state import *

from logs.logger_config import logger as logging
graph = build_graph()
def get_response(query, sender_id):
    try:
        if graph is None:
            raise Exception("Graph not initialized. Please initialize the graph first.")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        config = {
            "configurable": {
                "thread_id": sender_id,
            }
        }    
        state = {
            "messages":("user", query),
            "documents":"",
            "relevance":"",
            "answer": ""
        }
        logging.info(f"[{timestamp}] [GRAPH] State before invocation: {state}")
        
        response = graph.invoke(state,config)
        
        logging.info(f"[{timestamp}] [GRAPH] Response received: {response['answer']}")
        
        return response['answer']
    except Exception as e:
        logging.error(f"[{timestamp}] [ERROR] Chat error: {str(e)}", exc_info=True)
        return None