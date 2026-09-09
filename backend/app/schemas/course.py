from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class IGOTCourseResponse(BaseModel):
    id: int
    course_id: str
    title: str
    provider: str
    description: Optional[str] = None
    duration_hours: float
    competency_tags: str
    category: str
    difficulty: str
    language: str
    course_url: Optional[str] = None
    source: str
    active: bool

    class Config:
        from_attributes = True

class NSSTAProgrammeResponse(BaseModel):
    id: int
    training_id: str
    title: str
    provider: str
    description: Optional[str] = None
    duration_days: int
    duration_hours: float
    competency_tags: str
    category: str
    level: str
    target_audience: Optional[str] = None
    programme_url: Optional[str] = None
    source: str
    active: bool

    class Config:
        from_attributes = True

class CourseCatalogueResponse(BaseModel):
    total_igot_courses: int
    total_nssta_programmes: int
    igot_courses: List[IGOTCourseResponse]
    nssta_programmes: List[NSSTAProgrammeResponse]
