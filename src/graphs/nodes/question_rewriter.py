# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging


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

