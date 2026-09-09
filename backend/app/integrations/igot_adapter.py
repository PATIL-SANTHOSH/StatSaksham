from typing import List, Optional
from sqlalchemy.orm import Session
from app.integrations.base import BaseLearningProvider, StandardCourseItem
from app.models.course import IGOTCourse

class IGOTAdapter(BaseLearningProvider):
    def __init__(self, db: Session):
        self.db = db

    def get_provider_name(self) -> str:
        return "iGOT Karmayogi"

    def _to_standard_item(self, course: IGOTCourse) -> StandardCourseItem:
        tags = [t.strip() for t in course.competency_tags.split(",") if t.strip()]
        return StandardCourseItem(
            id=course.course_id,
            title=course.title,
            provider=course.provider,
            provider_type="iGOT",
            description=course.description or "",
            duration_hours=course.duration_hours,
            duration_label=f"{course.duration_hours:.1f} Hours",
            competency_tags=tags,
            category=course.category,
            difficulty=course.difficulty,
            level=course.difficulty,
            url=course.course_url,
            source=course.source,
            is_live_api=False
        )

    def search_courses(
        self,
        query: Optional[str] = None,
        competency_tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 50
    ) -> List[StandardCourseItem]:
        q = self.db.query(IGOTCourse).filter(IGOTCourse.active == True)
        
        if category and category.lower() != "all":
            q = q.filter(IGOTCourse.category.ilike(f"%{category}%"))
            
        if difficulty and difficulty.lower() != "all":
            q = q.filter(IGOTCourse.difficulty.ilike(f"%{difficulty}%"))
            
        if query:
            q = q.filter(
                (IGOTCourse.title.ilike(f"%{query}%")) |
                (IGOTCourse.description.ilike(f"%{query}%")) |
                (IGOTCourse.competency_tags.ilike(f"%{query}%"))
            )
            
        courses = q.limit(limit).all()
        
        # Filter by competency tags if provided
        if competency_tags:
            tag_set = {t.lower().strip() for t in competency_tags}
            matched_courses = []
            for c in courses:
                c_tags = {t.lower().strip() for t in c.competency_tags.split(",")}
                if tag_set.intersection(c_tags):
                    matched_courses.append(c)
            return [self._to_standard_item(c) for c in matched_courses]
            
        return [self._to_standard_item(c) for c in courses]

    def get_course_by_id(self, course_id: str) -> Optional[StandardCourseItem]:
        course = self.db.query(IGOTCourse).filter(IGOTCourse.course_id == course_id).first()
        if course:
            return self._to_standard_item(course)
        return None
