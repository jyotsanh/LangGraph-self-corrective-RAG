from core.state import *

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

# nodes
from graphs.nodes import *

# logs
from logs.logger_config import logger as logging
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def build_graph():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        builder = StateGraph(MyState)
        logging.info(f"[{timestamp}] [GRAPH] Starting graph construction...")
        logging.info(f"[{timestamp}] [GRAPH] Adding nodes to the graph...")
        builder.add_node("vectorstore",retriever)
        builder.add_node("web_search",web_search)
        
        builder.add_node("generate_response",generate_response)
        
        logging.info(f"[{timestamp}] [GRAPH] Adding conditional edges from START to query_analyser...")
        builder.add_conditional_edges(
            START,
            query_analyser,
            {
                "vectorstore": "vectorstore", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
                "web_search": "web_search", # -> if query analysis outputs web_search go to web_search_NODE
                "greet":"generate_response"
            }
            
        )
        
        logging.info(f"[{timestamp}] [GRAPH] Adding conditional edges from 'vectorstore' to check_relevance...")
        builder.add_node("rewrite_question",rewrite_question)
        
        builder.add_conditional_edges(
            "vectorstore",
            # {
            #     "yes": generate_response, # -> if check_relevance outputs yes go to vectorstore_NODE.
            #     "no": rewrite_question # -> if check_relevance outputs no go to rewrite_question
            # }
            check_relevance,
            {
                "yes": "generate_response", # -> if check_relevance outputs yes go to vectorstore_NODE.
                "no": "rewrite_question" # -> if check_relevance outputs no go to rewrite_question
            }
        )
        
        
        builder.add_edge("rewrite_question","vectorstore")
        builder.add_edge("web_search","generate_response")
        builder.add_edge("generate_response",END)
        
        
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