from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any

class UserProfile(BaseModel):
    name: str
    age: int
    email: str

class LoginRequest(BaseModel):
    name: str
    age: int
    email: str

class Question(BaseModel):
    id: str
    text: str
    domain: str
    type: str # 'text', 'button', 'drawing'
    input_type: str # 'text_input', 'button', 'drawing'
    points: int
    content: Optional[List[str]] = None
    button_text: Optional[str] = None

class AnswerRequest(BaseModel):
    question_id: str
    user_input: str
    duration: float
    session_id: str

class TypingMetrics(BaseModel):
    speed_wpm: float
    error_rate: float
    consistency: float

class AnswerResponse(BaseModel):
    score: float
    status: str # 'Correct', 'Partial', 'Incorrect'
    feedback: str
    earned_points: float
    typing_metrics: Dict[str, Any]
    next_question: Optional[Question] = None
    is_completed: bool = False

class AssessmentResult(BaseModel):
    total_score: float
    max_score: float
    disease_prediction: Dict[str, Any]
    typing_summary: Dict[str, Any]
    responses: List[Dict[str, Any]]
