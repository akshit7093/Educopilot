from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.services import agent_service
from backend.app.core import database_handler
from typing import List, Dict, Any, Optional

router = APIRouter()

# --- Pydantic Models ---
class ContentRequest(BaseModel):
    topic: str
    grade_level: str

class SupportRequest(BaseModel):
    topic: str
    quiz_score: int
    student_name: str
    student_performance_summary: str
    wrong_answers: List[Dict[str, Any]]

class SaveScoreRequest(BaseModel):
    student_id: int
    quiz_topic: str
    score_percent: int
    total_questions: int
    wrong_answers: List[Dict[str, Any]]

# --- API Endpoints ---
@router.post("/generate-content", tags=["Workflows"])
def generate_content_endpoint(request: ContentRequest):
    result = agent_service.run_content_generation(
        topic=request.topic, grade_level=request.grade_level
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result["data"]

@router.post("/generate-support", tags=["Workflows"])
def generate_support_endpoint(request: SupportRequest):
    result = agent_service.run_support_generation(
        topic=request.topic,
        quiz_score=request.quiz_score,
        student_name=request.student_name,
        student_performance_summary=request.student_performance_summary,
        wrong_answers=request.wrong_answers,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result["data"]

# In educopilot/backend/app/api/v1/endpoints/generation.py

@router.post("/save-score", tags=["Database"])
def save_score_endpoint(request: SaveScoreRequest):
    """
    Receives a student's quiz score and saves it to the database.
    """
    try:
        # Call the database handler with ALL the required arguments
        result = database_handler.save_quiz_result(
            student_id=request.student_id,
            quiz_topic=request.quiz_topic,
            score=request.score_percent,
            total_questions=request.total_questions,
            # --- THIS IS THE FIX ---
            wrong_answers=request.wrong_answers # Pass the wrong_answers from the request
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quiz-results", tags=["Database"])
def get_quiz_results_endpoint():
    """Retrieves all quiz results, wrapped in a consistent dictionary."""
    try:
        results = database_handler.get_quiz_results()
        # --- THIS IS THE FIX ---
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students", tags=["Database"])
def get_students_endpoint():
    """Retrieves all students, wrapped in a consistent dictionary."""
    try:
        students = database_handler.get_all_students()
        # --- THIS IS THE FIX ---
        return {"data": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))