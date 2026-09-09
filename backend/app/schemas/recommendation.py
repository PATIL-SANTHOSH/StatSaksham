from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RecommendationResponse(BaseModel):
    id: int
    employee_id: str
    course_type: str  # "iGOT" or "NSSTA"
    course_id: str
    title: str
    provider: str
    competency_name: str
    priority: str     # High, Medium, Low
    relevance_score: float
    relevance_label: str
    reason: str
    estimated_duration: str
    expected_competency_improvement: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RecommendationListResponse(BaseModel):
    employee_id: str
    total_recommendations: int
    high_priority_count: int
    igot_recommendations: List[RecommendationResponse]
    nssta_recommendations: List[RecommendationResponse]
    all_recommendations: List[RecommendationResponse]
