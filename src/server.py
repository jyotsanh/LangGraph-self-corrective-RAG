from fastapi import FastAPI
from routes.chat_routes import router as chat_router
from routes.update_routes import router as update_router

# logs
from logs.logger_config import logger

app = FastAPI(
    title="LangGraph based Self-Corrective RAG",
    description="Self-Corrective RAG made using LangGraph"
)

# Include chat routes
app.include_router(chat_router)

app.include_router(update_router)

logger.info("\nFastAPI app initialized successfully.\n")

# Optional: Add health check endpoint
@app.get("/")
async def health_check():
    response = {
                    "status": "healthy"
                }
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000,reload=True)