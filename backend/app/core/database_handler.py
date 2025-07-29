import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

DATABASE_FILE = Path(__file__).parent.parent.parent.parent / "database.json"

def _read_db() -> Dict:
    """Helper function to read the entire JSON database."""
    try:
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file is broken or not found, return a safe default structure
        return {"students": [], "quiz_results": []}

def _write_db(data: Dict):
    """Helper function to write data back to the JSON database."""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_all_students() -> List[Dict]:
    """Reads and returns the list of all students."""
    data = _read_db()
    return data.get("students", [])

def get_quiz_results() -> List[Dict]:
    """Reads and returns all saved quiz results."""
    data = _read_db()
    return data.get("quiz_results", [])

# --- THIS IS THE CORRECTED FUNCTION ---
def save_quiz_result(
    student_id: int, 
    quiz_topic: str, 
    score: int, 
    total_questions: int, 
    wrong_answers: List[Dict[str, Any]] # It now correctly accepts this parameter
):
    """Saves a new quiz result to the database."""
    db_data = _read_db()
    
    student_name = "Unknown"
    # Safely find the student name
    for student in db_data.get("students", []):
        if student.get('id') == student_id:
            student_name = student.get('name', "Unknown")
            break
            
    new_result = {
        "result_id": len(db_data.get("quiz_results", [])) + 1,
        "student_id": student_id,
        "student_name": student_name,
        "quiz_topic": quiz_topic,
        "score_percent": score,
        "total_questions": total_questions,
        "wrong_answers": wrong_answers, # The data is now correctly included
        "timestamp": datetime.now().isoformat()
    }
    
    # Ensure the quiz_results key exists before appending
    if "quiz_results" not in db_data:
        db_data["quiz_results"] = []
        
    db_data["quiz_results"].append(new_result)
    _write_db(db_data)
    return new_result