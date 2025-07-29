from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.services import agent_service

router = APIRouter()

class WorkflowRequest(BaseModel):
    """Defines the request body for running the workflow."""
    topic: str = Field(..., example="The Solar System")
    grade_level: str = Field(..., example="6th Grade")

@router.post("/generate-full-flow", response_model=dict)
def generate_full_workflow_endpoint(request: WorkflowRequest):
    """
    API endpoint to run the full workflow:
    1. Generate a lesson plan.
    2. Generate a quiz from that plan.
    """
    result = agent_service.run_lesson_to_quiz_workflow(
        topic=request.topic, 
        grade_level=request.grade_level
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
        
    return {
        "lesson_plan": result["lesson_plan"],
        "quiz": result["quiz"]
    }