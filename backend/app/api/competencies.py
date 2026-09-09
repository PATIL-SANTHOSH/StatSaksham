from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.competency import Competency, CompetencyRequirement
from app.schemas.competency import CompetencyResponse, CompetencyRequirementResponse, SkillGapResponse
from app.services.competency_service import CompetencyService
from app.services.skill_gap_service import SkillGapService
from app.api.deps import get_current_user

router = APIRouter(tags=["Competencies & Skill Gaps"])

@router.get("/competencies", response_model=List[CompetencyResponse])
def list_competencies(db: Session = Depends(get_db)):
    return db.query(Competency).order_by(Competency.category, Competency.name).all()

@router.get("/competencies/requirements", response_model=List[CompetencyRequirementResponse])
def list_role_requirements(db: Session = Depends(get_db)):
    records = db.query(CompetencyRequirement, Competency).join(
        Competency, CompetencyRequirement.competency_id == Competency.id
    ).all()
    results = []
    for req, comp in records:
        results.append(CompetencyRequirementResponse(
            id=req.id,
            job_role=req.job_role,
            department_code=req.department_code,
            competency_id=req.competency_id,
            competency_name=comp.name,
            category=comp.category,
            required_level=req.required_level,
            priority_weight=req.priority_weight,
            rationale=req.rationale
        ))
    return results

@router.get("/employees/{employee_id}/competencies")
def get_employee_competencies(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = CompetencyService(db)
    try:
        return service.get_employee_competencies(employee_id.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/employees/{employee_id}/skill-gaps", response_model=SkillGapResponse)
def get_employee_skill_gaps(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = SkillGapService(db)
    try:
        return service.calculate_skill_gaps(employee_id.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
