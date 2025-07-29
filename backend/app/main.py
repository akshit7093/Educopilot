from fastapi import FastAPI
from backend.app.api.v1.endpoints import generation # Import our new unified endpoint file

app = FastAPI(
    title="EduCopilot API",
    description="The backend API for the EduCopilot multi-agent system.",
    version="1.0.0"
)

# Include the new router with all our specialized endpoints
app.include_router(
    generation.router, 
    prefix="/api/v1/generate" # The base URL for all our actions
)

@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint for health checks.
    """
    return {"message": "Welcome to the EduCopilot API. The system is running."}