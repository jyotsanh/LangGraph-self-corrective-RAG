from core.state import *

from langchain_core.prompts import ChatPromptTemplate

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain_community.vectorstores import Chroma

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver

#libs
from libs.libs import *

from langchain_community.tools.tavily_search import TavilySearchResults

web_search_tool = TavilySearchResults(k=3)



def query_analyser(state:MyState)-> Literal["vectorstore", f"web_search"]:
    
    query = state['messages'][-1].content
    
    system_prompt =  """
                    You are an expert at routing a user question to a vectorstore or web search.
                    The vectorstore contains documents related to the following topics.
                    - Who created This Project
                    - Who is Jyotsan, His CV details.
                    - Game of Thrones
                    - The Lord of the Rings
                    - Star Wars
                    Use the vectorstore for questions on these topics. Otherwise, use web-search.
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
    return response.datasource

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

def retriever(state:MyState):
    
    pdf_path = state['./data/MyCV']  # Path to the PDF file
    loader = PyPDFLoader(pdf_path)
    docs_list = loader.load()  # Load documents from the PDF
    # Set embeddings
    embd = get_embedding(model="google")
    # Split
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=600, chunk_overlap=100
    )
    doc_splits = text_splitter.split_documents(docs_list)
    # Add to vectorstore
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embd,
    )
    retriever = vectorstore.as_retriever()
    
    query = state['messages'][-1].content
    docs = retriever.invoke(query)
    
    return {**state,"documents":docs}
    
def check_relevance(state:MyState)->Literal[f"generate_response", f"rewrite_question"]:
    system_prompt =    """
                       You are a grader assessing relevance of a retrieved document to a user question. \n 
                        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
                        It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
                        Give 'generate_response' or 'rewrite_question' score to indicate whether the document is relevant to the question.
                        """
                        
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )
    llm = get_llm(model="google",temperature=0)
    structured_llm_router = llm.with_structured_output(CheckRelevance)
    chain = grade_prompt | structured_llm_router
    
    document = state['documents']
    question = state['messages'][-1].content
    response = chain.invoke({"document":document,"question":question})
    
    return response.binary_score


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
    system_prompt = """
                    From the given Document, Act very friendly and respond like human friend, like you know the person. Answer User Queries.
                    """
    response_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )
    
    llm = get_llm(model="google",temperature=0.6)
    chain = response_prompt | llm
    chain_response = chain.invoke(
                {
                "document":document,
                "question":question
                }
                                  )
    return {**state,"answer":chain_response.content}
    

def build_graph():
    builder = StateGraph(MyState)
        
    builder.add_node("vectorstore",retriever)
    builder.add_node("web_search",web_search)
    
    builder.add_node("generate_response",generate_response)
    
    
    builder.add_conditional_edges(
        START,
        query_analyser,
        {
            "vectorstore": "vectorstore", # -> if query analysis outputs vectorestore store go to vectorstore_NODE.
            "web_search": "web_search", # -> if query analysis outputs web_search go to web_search_NODE
        }
        
    )
    builder.add_node("rewrite_question",rewrite_question)
       
    builder.add_conditional_edges(
        "vectorstore",
        # {
        #     "yes": generate_response, # -> if check_relevance outputs yes go to vectorstore_NODE.
        #     "no": rewrite_question # -> if check_relevance outputs no go to rewrite_question
        # }
        check_relevance,
        {
            "generate_response": "generate_response", # -> if check_relevance outputs yes go to vectorstore_NODE.
            "rewrite_question": "rewrite_question" # -> if check_relevance outputs no go to rewrite_question
        }
    )
    
    
    builder.add_edge("rewrite_question","vectorstore")
    builder.add_edge("web_search","generate_response")
    builder.add_edge("generate_response",END)
    
    ChatMemory = MemorySaver()
    graph = builder.compile(
            checkpointer = ChatMemory
        )
    # Visualize your graph
    from IPython.display import Image, display
    graph.get_graph().draw_mermaid_png(output_file_path="./graph.png")
        
    return graph