from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from backend.app.services import agent_service

router = APIRouter()

class QuizRequest(BaseModel):
    """Defines the request body for generating a quiz."""
    lesson_plan_content: str = Field(..., example="This is the full text of the lesson plan...")

@router.post("/generate", response_model=dict)
def generate_quiz_endpoint(request: QuizRequest):
    """
    API endpoint to generate a new quiz from a lesson plan.
    """
    result = agent_service.generate_quiz_from_plan(lesson_plan_content=request.lesson_plan_content)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
        
    return {"quiz": result["quiz"]}