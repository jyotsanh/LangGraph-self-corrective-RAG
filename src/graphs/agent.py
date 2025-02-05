# original
#from graphs.graph_builder import build_graph

# trial
from graphs.graph_builder2 import build_graph

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
        # state = {
        #     "messages":("user", query),
        #     "documents":"",
        #     "package_type":"",
        #     "package_name":"",
        #     "customer_motive":"",
        #     "customer_type":"",
        #     "answer": ""
        # }
        state = {
            "messages":("user", query),
            "answer": ""
        }
        logging.info(f"[{timestamp}] [GRAPH] State before invocation: {state}")
        
        response = graph.invoke(state,config)
        
        logging.info(f"[{timestamp}] [GRAPH] Response received: {response['answer']}")
        
        return response['messages'][-1].content
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.error(f"[{timestamp}] [ERROR] Chat error: {str(e)}", exc_info=True)
        return None
