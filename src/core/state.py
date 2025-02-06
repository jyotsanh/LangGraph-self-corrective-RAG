from enum import Enum
from typing import Annotated, List, Optional
from langgraph.graph.message import AnyMessage, add_messages
from typing_extensions import TypedDict

from libs.libs import *

class MyState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    package_name: Literal["home", "mobile",None]
    package_type: Literal["prepaid", "postpaid",None]
    customer_name: Optional[str]
    customer_package:Optional[str]
    customer_motive: Literal["suggestion", "upgrade",None]
    customer_type: Literal["old", "new","None"]
    documents: str
    answer: str
    
# Data model
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    datasource: Literal["vectorstore", "web_search","greet"] = Field(
        ...,
        description="Given a user question choose to route it to web search, vectorstore or a greet.",
    )
    
class CheckRelevance(BaseModel):
    """
    A model to determine the relevance of a document to the given query.

    Attributes:
        datasource (Literal["yes", "no"]): Indicates whether the document is relevant to the query.
            - "yes": The document is not relevant and should be routed to generate a response.
            - "no": The document is relevant and should be routed to re-write the question.
            
    """
    binary_score: Literal["yes", "no"] = Field(
        ...,
        description="Indicates if the document is relevant to the query. Choose 'not' to re-write the question or 'yes' to generate a response.",
    )

class RewriteQuestion(BaseModel):
    rewritten_question: str = Field(
        ...,
        description="Rewritten question based on the context of the document.",
    )

class VectorDB(Enum):
    CHROMA = "chroma"
    MILVUS = "milvus"
    
    
class StoreArguments(BaseModel):
    path: str = Field(
        ..., description="List of dictionaries containing data to store. Each dictionary should have a 'content' key with the actual content."
    )
    collection_name: str = Field(
        ..., description="Name of the collection to store the data in. Follows the format 'general_store_<id>'."
    )
    store_type: VectorDB = Field(
        ... , description="Type of vector store to use. "
    )
    embeddings:GoogleGenerativeAIEmbeddings = Field(..., description='embedding to be provided to vector store ')
    

class CollectInfo(BaseModel):
    """
    A model to determine the type of customer.

    Attributes:
        customer_type (Literal["old", "new","None"]): Indicates whether the customer is new, old and None.
    """
    customer_type: Literal["old", "new", "None"]


class IntrestedPackage(BaseModel):
    """
    A model to determine the name of package customer is intrested in.

    Attributes:
        package_name (Literal["home", "mobile","None"]): Indicates whether the customer is intrested in home, mobile or None.
    """
    package_name: Literal["home", "mobile","None"]


class HasUsername(BaseModel):
    """
    A model to determine if the conversation history has a customer username or not.
    
    Attributes:
        username (Union[Literal["ask_username"], str]): 
            Indicates whether the conversation history has a username or not.
            If not, "ask_username" is returned.
    """
    username: Union[Literal["ask_username"], str]


class BeSure(BaseModel):
    """
    A model to make sure customer is clear, on which package he is intrested in.
    
    Attributes:
        intrested_package (Literal["ask_username","unclear"]): 
            Indicates whether the customer is clear, on which package he is intrested in.
    """
    intrested_package: Literal["clear","unclear"]


class IntrestedPackageType(BaseModel):
    """
    A model to determine the type of package customer is intrested in.

    Attributes:
        package_type (Literal["prepaid", "postpaid","all","unclear"]): Indicates whether the customer is intrested in postpaid, prepaid , both or unclear.
    """
    package_type: Literal["prepaid", "postpaid","all","unclear"]
