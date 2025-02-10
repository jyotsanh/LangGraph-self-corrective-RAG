from fastapi import APIRouter, Query
from graphs.vector_updates import *
from pydantic import BaseModel
from fastapi import HTTPException
router = APIRouter(prefix="/update_vectore_store", tags=["Update"])

# libs
from libs.libs import *

#states
from core.state import *

# logs
import time
from logs.logger_config import logger as logging



@router.post("/", response_model=UpdateResponse)
async def update_endpoint(vector_store:VectorDB, senderId: str, collection_name: VectorCollection)-> UpdateResponse:
    start_time = time.time()
    
    update_functions = {
        VectorCollection.GeneralFAQ: general_update_function,
        VectorCollection.Mobile_Internet: mobile_internet_update_function,
        VectorCollection.Home_Internet: home_internet_update_function,
    }
    try:
        logging.info(f" [UPDATE] Received request to update vector store for sender ID: {senderId}")

        if collection_name.value == "all":
            update_function_responses = []
            for func in update_functions.values():
                vec_response = await func(
                     vector_store=vector_store,
                    senderId=senderId,
                    collection_name=collection_name
                )
                update_function_responses.append(vec_response)
            response = " ,".join(update_function_responses)
        else:
            if collection_name not in update_functions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid collection name: {collection_name}"
                )
            response = await update_functions[collection_name](
                    vector_store=vector_store,
                    senderId=senderId,
                    collection_name=collection_name
                )
       
        execution_time = time.time() - start_time

        logging.info(
            "[UPDATE SUCCESS] Vector store updated successfully!\n"
        )
        
        return UpdateResponse(msg=response)
    except HTTPException as he:
        raise he
    except Exception as e:
        error_message = (
            f"[UPDATE ERROR] Failed to update vector store\n"
        )
        logging.error(error_message)
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred during vector store update"
        )
