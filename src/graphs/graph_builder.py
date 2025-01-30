from core.state import *

from langchain_core.prompts import ChatPromptTemplate


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_community.vectorstores import Chroma

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

#libs
from libs.libs import *
from libs import *  

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyPDFLoader
web_search_tool = TavilySearchResults(k=3)

# logs
import time
from logs.logger_config import logger as logging
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def query_analyser(state:MyState,testing=False) -> Literal["vectorstore", "web_search","greet"]:
    try:
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

def web_search(state:MyState):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    question = state["messages"][-1].content

    # Web search
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)
    state = {**state,"documents": web_results.page_content}

    return state


def retriever(state: MyState):
    """
    Retrieves relevant documents based on the latest user message in the state.

    Args:
        state (MyState): The current application state containing messages.

    Returns:
        Dict[str, Any]: Updated state with retrieved documents.
    """
    pdf_path = './data/Profile.pdf'  # PDF file path
    try:
        # Load documents from the PDF
        docs_list = _load_pdf(pdf_path)

        # Initialize embeddings
        embd = get_embedding(model="openai")
        if embd is None:
            raise ValueError("Embeddings not found")

        # Process documents into chunks
        doc_splits = _split_documents(docs_list)
        print(len(doc_splits))
        # Create vector store and retriever
        retriever = _initialize_vectorstore(doc_splits, embd)

        # Extract latest user query safely
        test_query = state['messages'][-1].content
        docs = retriever.invoke(test_query)
        
        context = ""
        for doc in docs:
            context += doc.page_content
        print(f"document retrieved")
        return {**state,"documents":context}
    except Exception as e:
        print(e)
    
def check_relevance(state:MyState,testing=False)->Literal["yes", "no"]:
    print("checking the relevance of the document")
    retrieved_document = state['documents']
    print("\n ------\n")
    print(retrieved_document)
    print("\n ------\n")
    system_prompt =   f"""
                       You are a grader assessing relevance of a retrieved document to a user question. \n 
                        If you think you can answer the use question with given context then. grade it as relevant -> 'yes' otherwise 'no'. \n
                        The goal is to filter out erroneous retrievals. \n
                        Give 'yes' or 'no' score to indicate whether the document is relevant to the question.\n
                        Retrieved document: \n\n {retrieved_document} 
                        """
                        
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "User question: {question}"),
        ]
    )
    
    llm = get_llm(model="openai",temperature=0)
    structured_llm_router = llm.with_structured_output(CheckRelevance)
    chain = grade_prompt | structured_llm_router
    print(f"\n {state} \n")
    
    if testing:
        question = state['messages'][-1]
    else:
        question = state['messages'][-1].content
    try:
        response = chain.invoke({"question": question})
        print(f"relevance score: {response.binary_score}")
        return response.binary_score
    except Exception as e:
        print(f"Error: {e}")


def rewrite_question(state:MyState):
    question = state["messages"][-1].content
    system_prompt = """
                    You are an expert at rephrasing a user question.
                    The vectorstore contains documents related to the following topics.
                    - Who created This Project
                    - Who is Jyotsan, His CV details.
                    - Game of Thrones
                    - The Lord of the Rings
                    - Star Wars
                    the user query is not able to retrieve the relevant document from the vectore rewrite the question.
                    """
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{question}"),
        ]
    )
    llm = get_llm(model="google",temperature=0)
    structured_llm_router = llm.with_structured_output(RewriteQuestion)
    chain = rewrite_prompt | structured_llm_router
    chain_response = chain.invoke({"question":question})
    state["messages"][-1].content = chain_response.rewritten_question
    return state

def generate_response(state:MyState):
    question = state['messages'][-1].content
    document = state['documents']
    system_prompt = f"""
                    From the given Document, Act very friendly and respond like human friend.\n
                    and Give the answer in less than 100 words.\n
                    Don't Answer Like: `They also know`,`they are `\n
                    Context: \n\n {document}
                    """
    response_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "User question: {question}"),
        ]
    )
    
    llm = get_llm(model="openai",temperature=0.6)
    chain = response_prompt | llm
    chain_response = chain.invoke(
                {
                "question":question
                }
    )
    print(chain_response.content)
    print("hehe")
    return {**state,"answer":chain_response.content}
    
from datetime import datetime
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