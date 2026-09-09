from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LearningProgressCreate(BaseModel):
    employee_id: str
    course_type: str  # "iGOT" or "NSSTA"
    course_id: str
    title: str
    provider: str
    competency_name: Optional[str] = None

class LearningProgressUpdate(BaseModel):
    status: Optional[str] = None  # Enrolled, In Progress, Completed
    progress_percentage: Optional[float] = None
    hours_spent: Optional[float] = None

class LearningProgressResponse(BaseModel):
    id: int
    employee_id: str
    course_type: str
    course_id: str
    title: str
    provider: str
    status: str
    progress_percentage: float
    hours_spent: float
    competency_name: Optional[str] = None
    competency_gain_applied: bool
    enrolled_date: datetime
    completed_date: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmployeeProgressSummary(BaseModel):
    employee_id: str
    total_enrolled: int
    in_progress_count: int
    completed_count: int
    total_learning_hours: float
    recent_activities: List[LearningProgressResponse]
