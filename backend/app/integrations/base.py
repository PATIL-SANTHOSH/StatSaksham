from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class StandardCourseItem(BaseModel):
    id: str
    title: str
    provider: str
    provider_type: str  # "iGOT" or "NSSTA"
    description: str
    duration_hours: float
    duration_label: str
    competency_tags: List[str]
    category: str
    difficulty: str
    level: str
    url: Optional[str] = None
    source: str
    is_live_api: bool = False

class BaseLearningProvider(ABC):
    @abstractmethod
    def search_courses(
        self,
        query: Optional[str] = None,
        competency_tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 50
    ) -> List[StandardCourseItem]:
        """Search available courses in provider catalogue"""
        pass

    @abstractmethod
    def get_course_by_id(self, course_id: str) -> Optional[StandardCourseItem]:
        """Fetch single course details by ID"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider brand name"""
        pass
