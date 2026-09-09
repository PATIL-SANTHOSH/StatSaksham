from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    email: str
    department: str
    department_code: Optional[str] = None
    designation: str
    job_role: str
    current_assignment: str
    education: str
    years_of_experience: float
    joining_date: Optional[date] = None
    previous_trainings: Optional[str] = None
    competency_domain: Optional[str] = "Statistical"
    role: Optional[str] = "LEARNER"
    profile_photo_url: Optional[str] = None

class EmployeeUpdate(BaseModel):
    current_assignment: Optional[str] = None
    education: Optional[str] = None
    previous_trainings: Optional[str] = None
    competency_domain: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[EmployeeResponse]
