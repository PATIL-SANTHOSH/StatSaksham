from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AssessmentQuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str
    competency_id: Optional[int] = None

    class Config:
        from_attributes = True

class AssessmentSummary(BaseModel):
    id: int
    code: str
    title: str
    category: str
    competency_id: Optional[int] = None
    competency_name: Optional[str] = None
    description: Optional[str] = None
    total_questions: int
    passing_score: float
    time_limit_minutes: int
    difficulty: str
    is_active: bool

    class Config:
        from_attributes = True

class AssessmentDetail(AssessmentSummary):
    questions: List[AssessmentQuestionResponse]

class AssessmentSubmitAnswer(BaseModel):
    question_id: int
    selected_option: str  # A, B, C, D

class AssessmentSubmitRequest(BaseModel):
    employee_id: str
    answers: List[AssessmentSubmitAnswer]

class QuestionFeedback(BaseModel):
    question_id: int
    question_text: str
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: Optional[str] = None

class AssessmentResultResponse(BaseModel):
    result_id: int
    employee_id: str
    assessment_id: int
    assessment_title: str
    competency_name: str
    total_questions: int
    correct_count: int
    score_percentage: float
    passed: bool
    previous_level: int
    new_level: int
    level_improved: bool
    feedback: List[QuestionFeedback]
    completed_at: datetime
