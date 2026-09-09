from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class QuizGenerateRequest(BaseModel):
    document_id: Optional[int] = None
    competency: str = "General Statistics"
    difficulty: str = "Intermediate"
    num_questions: int = 5
    raw_text: Optional[str] = None

class QuizDocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size_kb: float
    uploaded_by: str
    competency_tag: str
    title: str
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class QuizQuestionResponse(BaseModel):
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    competency: str
    difficulty: str
    source_reference: Optional[str] = None

    class Config:
        from_attributes = True

class QuizSubmitAnswer(BaseModel):
    question_id: int
    selected_option: str  # A, B, C, D

class QuizSubmitRequest(BaseModel):
    employee_id: str
    document_id: Optional[int] = None
    competency: str
    answers: List[QuizSubmitAnswer]

class QuizFeedbackItem(BaseModel):
    question_id: int
    question_text: str
    selected_option: str
    correct_option: str
    is_correct: bool
    explanation: Optional[str] = None
    source_reference: Optional[str] = None

class QuizResultResponse(BaseModel):
    attempt_id: int
    employee_id: str
    competency: str
    difficulty: str
    total_questions: int
    correct_count: int
    score_percentage: float
    passed: bool
    competency_updated: bool
    new_competency_level: Optional[int] = None
    feedback: List[QuizFeedbackItem]
    attempted_at: datetime
