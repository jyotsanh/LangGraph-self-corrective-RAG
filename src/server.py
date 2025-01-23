from fastapi import FastAPI
from routes.chat_routes import router as chat_router

app = FastAPI(
    title="LangGraph based Self-Corrective RAG",
    description="Self-Corrective RAG made using LangGraph"
)

# Include chat routes
app.include_router(chat_router)

# Optional: Add health check endpoint
@app.get("/")
async def health_check():
    response = {
                    "status": "healthy"
                }
    return response