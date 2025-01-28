from graphs.graph_builder import build_graph

#libs
from libs.libs import *

#state
from core.state import *

graph = build_graph()
def get_response(query, sender_id):
    
        
    config = {
        "configurable": {
            "thread_id": sender_id,
        }
    }    
    state = MyState(
        messages=[f"{query}"],
        documents="",
        relevance="",
        answer= ""
                    )

    response = graph.invoke(state,config)
    return response['messages'][-1]