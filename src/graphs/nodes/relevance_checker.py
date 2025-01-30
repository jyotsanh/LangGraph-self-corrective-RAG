# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging


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
