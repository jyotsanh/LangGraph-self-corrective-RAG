# core states
from core.state import *

# all important libs and functions
from libs.libs import *

# logs 
from logs.logger_config import logger as logging

from libs import *

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