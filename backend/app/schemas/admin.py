from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class CompetencyDistributionItem(BaseModel):
    competency_name: str
    category: str
    beginner_count: int      # level 1-2
    intermediate_count: int  # level 3
    advanced_count: int      # level 4-5
    average_level: float

class DepartmentSkillGapItem(BaseModel):
    department: str
    department_code: str
    employee_count: int
    employees_with_gaps: int
    average_gap: float
    high_priority_gaps: int
    top_gap_competencies: List[str]

class TopSkillGapMetric(BaseModel):
    competency_name: str
    category: str
    affected_employees_count: int
    average_gap: float
    priority: str

class LearningProgressMetric(BaseModel):
    course_type: str
    total_enrollments: int
    completed_count: int
    in_progress_count: int
    completion_rate_percentage: float

class WorkforceAnalyticsResponse(BaseModel):
    total_employees: int
    active_employees: int
    employees_with_skill_gaps: int
    total_skill_gaps_identified: int
    high_priority_gaps_count: int
    courses_recommended_count: int
    courses_enrolled_count: int
    courses_completed_count: int
    average_competency_improvement: float
    workforce_readiness_score: float
    top_skill_gaps: List[TopSkillGapMetric]
    department_summaries: List[DepartmentSkillGapItem]
    competency_distributions: List[CompetencyDistributionItem]
    learning_progress_metrics: List[LearningProgressMetric]
