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


def build_graph():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        builder = StateGraph(MyState)

        logging.info(f"[{timestamp}] [GRAPH] Starting graph construction...")
        logging.info(f"[{timestamp}] [GRAPH] Adding nodes to the graph...")

        builder.add_node("collection_info",collection_info)

        

        builder.add_node("ask_node",ask_node)
       
        
        builder.add_node("query_analyser",query_analyser)
        builder.add_node("has_username",has_username)
        

        builder.add_edge(START,"collection_info")

        builder.add_conditional_edges(
            "collection_info",
            lambda state: state.get("customer_type", ""),
            {
                "new": "query_analyser", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
                "old": "has_username", # -> if query analysis outputs web_search go to web_search_NODE
                "None":"ask_node"
            }
            
        )

        ####  HANDLES THE `NEW` CUSTOMER ####
        builder.add_node("findout_intrested_package",findout_intrested_package)

        builder.add_conditional_edges(
            "query_analyser",
            lambda state: state.get("package_name", ""), # Extracting the correct key
            {
                "home": "Home_Internet", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
                "mobile": "Mobile_Internet", # -> if query analysis outputs web_search go to web_search_NODE,
                "None":"findout_intrested_package"
                
            }
            
        )
        ####ENDING HANDLES THE `NEW` CUSTOMER ####
        
        ### BEGINNING HANDLES THE `OLD` CUSTOMER ####
        builder.add_node("fetch_customer_package",fetch_customer_package)
        builder.add_node("ask_customer_username",ask_customer_username)

        builder.add_conditional_edges(
                "has_username",
                lambda state: state.get("go_to", ""),
                {
                    "ask_username":"ask_customer_username",
                    "fetch_customer_package":"fetch_customer_package"
                }
            )
        ### ENDING HANDLES THE `OLD` CUSTOMER ####

        builder.add_node("make_sure_intrested_package",make_sure_package)

        builder.add_edge("fetch_customer_package","make_sure_intrested_package")

        builder.add_conditional_edges(
            "make_sure_intrested_package",
            lambda state: state.get("intrested_package", ""),
            {   
                "clear":"query_analyser",
                "unclear":"findout_intrested_package",
                
            }
        )


        builder.add_node("pre_paid_internet",pre_paid_internet)
        builder.add_node("post_paid_internet",post_paid_internet)

        builder.add_node("find_out_package_type",find_out_package_type)
        builder.add_node("all_home_packages",all_home_packages)
        ##### Beginning of Home Internet packages ####

        builder.add_node("Home_Internet",home_internet)
        builder.add_conditional_edges(
            "Home_Internet",
            lambda state: state.get("package_type", ""),
            {
                "all": "all_home_packages",
                "prepaid":"pre_paid_internet",
                "postpaid":"post_paid_internet",
                "unclear": "find_out_package_type",
                
            }
        )

        ##### Ending of Home Internet packages ####

        #### Beginning of Mobile Internet packages ####
        builder.add_node("Mobile_Internet",mobile_internet)

        builder.add_conditional_edges(
            "Mobile_Internet",
            lambda state: state.get("package_type", ""),
            {
                "all": "all_home_packages",
                "prepaid":"pre_paid_internet",
                "postpaid":"post_paid_internet",
                
                "unclear": "find_out_package_type",
                
            }
        )
        ### Ending of Mobile Internet packages ####


        builder.add_node("check_relevance",check_relevance)

        builder.add_node("generate_response",generate_response)

        # builder.add_node("re_write_question",re_write_question)

        builder.add_edge("all_home_packages","check_relevance")
        builder.add_edge("pre_paid_internet","check_relevance")
        builder.add_edge("post_paid_internet","check_relevance")
        builder.add_edge("find_out_package_type","check_relevance")

        builder.add_edge("check_relevance","generate_response")
        builder.add_edge("generate_response",END)

        builder.add_edge("ask_customer_username",END)

        

        # builder.add_edge("fetch_customer_package",END)
        builder.add_edge("findout_intrested_package",END)
        builder.add_edge("ask_node",END)
        # builder.add_edge("fetch_customer_package",END)

        logging.info(f"[{timestamp}] [GRAPH] Initializing chat memory and compiling graph...")

        ChatMemory = MemorySaver()
        graph = builder.compile(
                checkpointer = ChatMemory
            )
        # Visualize your graph
        from IPython.display import Image, display
        graph.get_graph().draw_mermaid_png(output_file_path="./graph.png")
        logging.info("Graph Building.... **Sucessfull**")
        return graph
    except Exception as e:
        logging.info(f"Error: {e}")
        return None