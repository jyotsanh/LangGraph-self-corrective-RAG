
# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging



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
