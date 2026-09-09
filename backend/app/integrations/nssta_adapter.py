from typing import List, Optional
from sqlalchemy.orm import Session
from app.integrations.base import BaseLearningProvider, StandardCourseItem
from app.models.course import NSSTAProgramme

class NSSTAAdapter(BaseLearningProvider):
    def __init__(self, db: Session):
        self.db = db

    def get_provider_name(self) -> str:
        return "NSSTA / TPAC"

    def _to_standard_item(self, prog: NSSTAProgramme) -> StandardCourseItem:
        tags = [t.strip() for t in prog.competency_tags.split(",") if t.strip()]
        return StandardCourseItem(
            id=prog.training_id,
            title=prog.title,
            provider=prog.provider,
            provider_type="NSSTA",
            description=prog.description or "",
            duration_hours=prog.duration_hours,
            duration_label=f"{prog.duration_days} Days ({prog.duration_hours:.0f} Hrs)",
            competency_tags=tags,
            category=prog.category,
            difficulty=prog.level,
            level=prog.level,
            url=prog.programme_url,
            source=prog.source,
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
        q = self.db.query(NSSTAProgramme).filter(NSSTAProgramme.active == True)
        
        if category and category.lower() != "all":
            q = q.filter(NSSTAProgramme.category.ilike(f"%{category}%"))
            
        if difficulty and difficulty.lower() != "all":
            q = q.filter(NSSTAProgramme.level.ilike(f"%{difficulty}%"))
            
        if query:
            q = q.filter(
                (NSSTAProgramme.title.ilike(f"%{query}%")) |
                (NSSTAProgramme.description.ilike(f"%{query}%")) |
                (NSSTAProgramme.competency_tags.ilike(f"%{query}%"))
            )
            
        progs = q.limit(limit).all()
        
        if competency_tags:
            tag_set = {t.lower().strip() for t in competency_tags}
            matched = []
            for p in progs:
                p_tags = {t.lower().strip() for t in p.competency_tags.split(",")}
                if tag_set.intersection(p_tags):
                    matched.append(p)
            return [self._to_standard_item(p) for p in matched]
            
        return [self._to_standard_item(p) for p in progs]

    def get_course_by_id(self, training_id: str) -> Optional[StandardCourseItem]:
        prog = self.db.query(NSSTAProgramme).filter(NSSTAProgramme.training_id == training_id).first()
        if prog:
            return self._to_standard_item(prog)
        return None
