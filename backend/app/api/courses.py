from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.course import IGOTCourse, NSSTAProgramme
from app.schemas.course import IGOTCourseResponse, NSSTAProgrammeResponse, CourseCatalogueResponse

router = APIRouter(prefix="/courses", tags=["Courses & Catalogues"])

@router.get("/igot", response_model=List[IGOTCourseResponse])
def list_igot_courses(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(IGOTCourse).filter(IGOTCourse.active == True)
    if category and category.lower() != "all":
        q = q.filter(IGOTCourse.category.ilike(f"%{category}%"))
    if difficulty and difficulty.lower() != "all":
        q = q.filter(IGOTCourse.difficulty.ilike(f"%{difficulty}%"))
    if query:
        s = f"%{query}%"
        q = q.filter((IGOTCourse.title.ilike(s)) | (IGOTCourse.competency_tags.ilike(s)))
    return q.limit(limit).all()

@router.get("/nssta", response_model=List[NSSTAProgrammeResponse])
def list_nssta_programmes(
    category: Optional[str] = None,
    level: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(NSSTAProgramme).filter(NSSTAProgramme.active == True)
    if category and category.lower() != "all":
        q = q.filter(NSSTAProgramme.category.ilike(f"%{category}%"))
    if level and level.lower() != "all":
        q = q.filter(NSSTAProgramme.level.ilike(f"%{level}%"))
    if query:
        s = f"%{query}%"
        q = q.filter((NSSTAProgramme.title.ilike(s)) | (NSSTAProgramme.competency_tags.ilike(s)))
    return q.limit(limit).all()

@router.get("/catalogue", response_model=CourseCatalogueResponse)
def get_full_catalogue(db: Session = Depends(get_db)):
    igot_list = db.query(IGOTCourse).filter(IGOTCourse.active == True).all()
    nssta_list = db.query(NSSTAProgramme).filter(NSSTAProgramme.active == True).all()
    return CourseCatalogueResponse(
        total_igot_courses=len(igot_list),
        total_nssta_programmes=len(nssta_list),
        igot_courses=igot_list,
        nssta_programmes=nssta_list
    )

@router.get("/{course_type}/{course_id}")
def get_course_details(course_type: str, course_id: str, db: Session = Depends(get_db)):
    c_type = course_type.upper()
    if c_type == "IGOT":
        c = db.query(IGOTCourse).filter(IGOTCourse.course_id == course_id).first()
        if not c:
            raise HTTPException(status_code=404, detail="iGOT Course not found")
        return {"type": "iGOT", "data": c}
    elif c_type == "NSSTA":
        p = db.query(NSSTAProgramme).filter(NSSTAProgramme.training_id == course_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="NSSTA Programme not found")
        return {"type": "NSSTA", "data": p}
    else:
        raise HTTPException(status_code=400, detail="Invalid course type. Use 'igot' or 'nssta'")
