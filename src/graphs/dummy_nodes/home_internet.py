# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

# db
from models.db import *

def home_internet(state:MyState,testing=False)-> Literal["prepaid", "postpaid","all","unclear"]:
    try:
        # Validate state input
        if not state or "messages" not in state or not state["messages"]:
            raise ValueError("Invalid state: 'messages' is missing or empty")
        
        if testing:
            query = state['messages'][-1]
            conversation_history = "\n".join([msg for msg in state['messages']])
        else:
            query = state["messages"][-1].content
            conversation_history = "\n".join([msg.content for msg in state['messages']])

            
        if state['package_name'] == 'home':
            system_prompt =  f"""
                            
                            Analyse the given conversation_history and Determine if the user is intrested in prepaid or postpaid package type.\n
                            if the user wants to know both package type then answer -> all \n
                            if you can't detemine the package type with conversation_history then answer -> 'None'. \n

                            Consider this while analyzing the  conversation_history:\n
                                - if you see pre-paid and post-paid keywords in conversation_history, don't assume that user is intrested in both packages.\n
                                - the user must say , he is intrested in both packages in one sentence, then only you can consider that user is intrested in both packages. \n
                                - Assume that user is intrested in that packages which is most-recent.
                                """
            route_prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{conversation_history}"),
                ]
            )
                
            # LLM with function call
            llm = get_llm(model="google",temperature=0)
            structured_llm_router = llm.with_structured_output(IntrestedPackageType)
            chain = route_prompt | structured_llm_router
            
            response = chain.invoke({"conversation_history": conversation_history})
            # Log routing decision
            logging.info(f"Query: {query} -> Routing to: {response.package_type}")
            
            if response.package_type in ["prepaid", "postpaid","all","unclear"]:
                state = {**state,"package_type": response.package_type}
                return state
            else:
                raise Exception("Package type not in ['prepaid','postpaid','all','unclear']")
    except Exception as e:
        logging.error(f"FILE ['home_internet'->home_internet] [ERROR] Chat error: {str(e)}", exc_info=True)


from langchain.schema import AIMessage  # Import AIMessage


def similarity_search_func(query,package_name):
    if package_name == 'home':
        
        collection_name=os.getenv("Home_Internet_STC")
    elif package_name == 'mobile':
        collection_name = os.getenv("Mobile_Internet_STC")
    logging.info(f"[DOC] Collection name : {collection_name} of {package_name} internet")
    open_embeddings = get_embedding("openai")
    vector_store = VectorStore(
                                    collection_name=collection_name, 
                                    store_type="milvus", 
                                    embeddings =open_embeddings
                                    ).get_vector_store()
    docs = vector_store.similarity_search(query=query,k=3)
    return docs

def both_package_type(state:MyState,testing=False):
    try:
        if state.get('documents',None)==None: # in case the documents is None.

            package_name = state['package_name'] # -> home or mobile

            # package_type = state['package_type'] # -> all
            packages_type = ['prepaid','postpaid']

            both_package_context = []
            for package in packages_type:
                query = f"Provide all the package details about {package_name} internet , {package} packages"
                similar_docs = similarity_search_func(query,package_name)
                both_package_context.append(similar_docs)

            logging.info(f"{state['package_name']} both package, fetched docs and going to -> check relevance")
            state = {**state,"documents": both_package_context}
            return state
        else: # if again user wants to know both package type then why do a similarity search ..
            return state
        
    except Exception as e:
        logging.error(f"FILE ['home_internet'->both_package_type] [ERROR] Chat error: {str(e)}", exc_info=True)