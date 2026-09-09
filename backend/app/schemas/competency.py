from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CompetencyResponse(BaseModel):
    id: int
    code: str
    name: str
    category: str
    description: Optional[str] = None
    domain: Optional[str] = None
    max_level: int = 5

    class Config:
        from_attributes = True

class CompetencyRequirementResponse(BaseModel):
    id: int
    job_role: str
    department_code: Optional[str] = None
    competency_id: int
    competency_name: Optional[str] = None
    category: Optional[str] = None
    required_level: int
    priority_weight: int
    rationale: Optional[str] = None

    class Config:
        from_attributes = True

class EmployeeCompetencyResponse(BaseModel):
    id: int
    employee_id: str
    competency_id: int
    competency_name: str
    category: str
    current_level: int
    assessed_level: int
    last_assessed_date: Optional[datetime] = None
    verified_by_assessment: bool
    source: str

    class Config:
        from_attributes = True

class SkillGapItem(BaseModel):
    competency_id: int
    competency_code: str
    competency_name: str
    category: str
    current_level: int
    required_level: int
    gap: int
    gap_category: str  # No Gap, Low Gap, Medium Gap, High Gap
    priority: str      # High, Medium, Low, None
    priority_score: float
    importance_weight: int
    reason: str
    recommended_action: str

class SkillGapResponse(BaseModel):
    employee_id: str
    employee_name: str
    job_role: str
    department: str
    current_assignment: str
    total_competencies: int
    total_gaps: int
    high_priority_gaps_count: int
    medium_priority_gaps_count: int
    low_priority_gaps_count: int
    average_gap: float
    overall_readiness_percentage: float
    gaps: List[SkillGapItem]
