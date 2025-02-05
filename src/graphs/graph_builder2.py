from core.state import *

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

# # nodes
# from graphs.nodes import *

# dummy nodes
from graphs.dummy_nodes import *

# logs
from logs.logger_config import logger as logging
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def test_response(state:MyState,testing=False):
    state = {**state,"messages": f"so you  are intrested in {state['package_name']} packages"}
    return state

def build_graph():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        builder = StateGraph(MyState)

        logging.info(f"[{timestamp}] [GRAPH] Starting graph construction...")
        logging.info(f"[{timestamp}] [GRAPH] Adding nodes to the graph...")

        builder.add_node("collection_info",collection_info)

        

        builder.add_node("ask_node",ask_node)
        builder.add_node("ask_username",ask_username)

        builder.add_node("query_analyser",query_analyser)

        

        builder.add_edge(START,"collection_info")

        builder.add_conditional_edges(
            "collection_info",
            lambda state: state.get("customer_type", ""),
            {
                "new": "query_analyser", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
                "old": "ask_username", # -> if query analysis outputs web_search go to web_search_NODE
                "None":"ask_node"
            }
            
        )

        ####  HANDLES THE `NEW` CUSTOMER ####
        builder.add_node("findout_intrested_package",findout_intrested_package)
        builder.add_node("test_response",test_response)

        builder.add_conditional_edges(
            "query_analyser",
            lambda state: state.get("package_name", ""), # Extracting the correct key
            {
                "home": "test_response", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
                "mobile": "test_response", # -> if query analysis outputs web_search go to web_search_NODE,
                "None":"findout_intrested_package"
                
            }
            
        )
        ####ENDING HANDLES THE `NEW` CUSTOMER ####
        
        ### BEGINNING HANDLES THE `OLD` CUSTOMER ####
        # builder.add_conditional_edges(
        #     "ask_username",
        #     lambda state: state.get("customer_package", ""), # Extracting the correct key
        #     {
        #         "home": "test_response", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
        #         "mobile": "test_response", # -> if query analysis outputs web_search go to web_search_NODE,
        #         "None":"findout_intrested_package"
                
        #     }
            
        # )
        ### ENDING HANDLES THE `OLD` CUSTOMER ####


        builder.add_edge("findout_intrested_package",END)
        builder.add_edge("ask_node",END)
        builder.add_edge("test_response",END)
        builder.add_edge("ask_username",END)

        logging.info(f"[{timestamp}] [GRAPH] Initializing chat memory and compiling graph...")

        ChatMemory = MemorySaver()
        graph = builder.compile(
                checkpointer = ChatMemory
            )
        # Visualize your graph
        # from IPython.display import Image, display
        # graph.get_graph().draw_mermaid_png(output_file_path="./graph.png")
        logging.info("Graph Building.... **Sucessfull**")
        return graph
    except Exception as e:
        logging.info(f"Error: {e}")
        return None