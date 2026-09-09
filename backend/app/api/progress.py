from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from app.database.session import get_db
from app.models.progress import LearningProgress
from app.models.competency import Competency, EmployeeCompetency
from app.schemas.progress import (
    LearningProgressCreate,
    LearningProgressUpdate,
    LearningProgressResponse,
    EmployeeProgressSummary
)
from app.api.deps import get_current_user

router = APIRouter(tags=["Learning Progress"])

@router.get("/employees/{employee_id}/progress", response_model=EmployeeProgressSummary)
def get_employee_progress(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    records = db.query(LearningProgress).filter(
        LearningProgress.employee_id == employee_id.upper()
    ).order_by(LearningProgress.updated_at.desc()).all()

    total_enrolled = len(records)
    in_progress = sum(1 for r in records if r.status == "In Progress")
    completed = sum(1 for r in records if r.status == "Completed")
    total_hours = sum(r.hours_spent for r in records)

    return EmployeeProgressSummary(
        employee_id=employee_id.upper(),
        total_enrolled=total_enrolled,
        in_progress_count=in_progress,
        completed_count=completed,
        total_learning_hours=round(total_hours, 1),
        recent_activities=records
    )

@router.post("/progress", response_model=LearningProgressResponse)
def enroll_or_update_progress(
    payload: LearningProgressCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    emp_id = payload.employee_id.upper()
    
    # Check if already enrolled
    prog = db.query(LearningProgress).filter(
        LearningProgress.employee_id == emp_id,
        LearningProgress.course_id == payload.course_id
    ).first()

    if not prog:
        prog = LearningProgress(
            employee_id=emp_id,
            course_type=payload.course_type,
            course_id=payload.course_id,
            title=payload.title,
            provider=payload.provider,
            status="In Progress",
            progress_percentage=10.0,
            hours_spent=1.0,
            competency_name=payload.competency_name,
            enrolled_date=datetime.now(timezone.utc)
        )
        db.add(prog)
    else:
        # Advance progress
        if prog.status == "Enrolled":
            prog.status = "In Progress"
            prog.progress_percentage = 25.0
            prog.hours_spent = max(1.0, prog.hours_spent)
        elif prog.status == "In Progress":
            # Progress towards completion
            prog.progress_percentage = min(100.0, prog.progress_percentage + 40.0)
            prog.hours_spent += 2.0
            if prog.progress_percentage >= 100.0:
                prog.status = "Completed"
                prog.completed_date = datetime.now(timezone.utc)

    # If completed and competency is specified, apply competency level bump (+1)
    if prog.status == "Completed" and not prog.competency_gain_applied and prog.competency_name:
        comp = db.query(Competency).filter(Competency.name.ilike(f"%{prog.competency_name}%")).first()
        if comp:
            ec = db.query(EmployeeCompetency).filter(
                EmployeeCompetency.employee_id == emp_id,
                EmployeeCompetency.competency_id == comp.id
            ).first()
            if ec:
                ec.current_level = min(5, ec.current_level + 1)
                ec.last_assessed_date = datetime.now(timezone.utc)
                ec.source = f"Completed {payload.course_type} Course"
            else:
                ec = EmployeeCompetency(
                    employee_id=emp_id,
                    competency_id=comp.id,
                    current_level=2,
                    assessed_level=2,
                    source=f"Completed {payload.course_type} Course"
                )
                db.add(ec)
        prog.competency_gain_applied = True

    db.commit()
    db.refresh(prog)
    return prog

@router.put("/progress/{progress_id}", response_model=LearningProgressResponse)
def update_progress_direct(
    progress_id: int,
    payload: LearningProgressUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    prog = db.query(LearningProgress).filter(LearningProgress.id == progress_id).first()
    if not prog:
        raise HTTPException(status_code=404, detail="Progress record not found")

    if payload.status:
        prog.status = payload.status
        if payload.status == "Completed" and not prog.completed_date:
            prog.completed_date = datetime.now(timezone.utc)
            prog.progress_percentage = 100.0

    if payload.progress_percentage is not None:
        prog.progress_percentage = payload.progress_percentage
        if prog.progress_percentage >= 100.0 and prog.status != "Completed":
            prog.status = "Completed"
            prog.completed_date = datetime.now(timezone.utc)

    if payload.hours_spent is not None:
        prog.hours_spent = payload.hours_spent

    db.commit()
    db.refresh(prog)
    return prog
