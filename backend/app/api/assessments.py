from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.assessment import Assessment, AssessmentQuestion
from app.models.competency import Competency
from app.schemas.assessment import (
    AssessmentSummary,
    AssessmentDetail,
    AssessmentQuestionResponse,
    AssessmentSubmitRequest,
    AssessmentResultResponse
)
from app.services.competency_service import CompetencyService
from app.api.deps import get_current_user

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("", response_model=List[AssessmentSummary])
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.is_active == True).all()
    results = []
    for a in assessments:
        comp_name = None
        if a.competency_id:
            c = db.query(Competency).filter(Competency.id == a.competency_id).first()
            if c:
                comp_name = c.name
        
        results.append(AssessmentSummary(
            id=a.id,
            code=a.code,
            title=a.title,
            category=a.category,
            competency_id=a.competency_id,
            competency_name=comp_name,
            description=a.description,
            total_questions=a.total_questions,
            passing_score=a.passing_score,
            time_limit_minutes=a.time_limit_minutes,
            difficulty=a.difficulty,
            is_active=a.is_active
        ))
    return results

@router.get("/{assessment_id}", response_model=AssessmentDetail)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    a = db.query(Assessment).filter(Assessment.id == assessment_id, Assessment.is_active == True).first()
    if not a:
        raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")

    questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == a.id).all()
    comp_name = None
    if a.competency_id:
        c = db.query(Competency).filter(Competency.id == a.competency_id).first()
        if c:
            comp_name = c.name

    q_responses = [
        AssessmentQuestionResponse(
            id=q.id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            difficulty=q.difficulty,
            competency_id=q.competency_id
        ) for q in questions
    ]

    return AssessmentDetail(
        id=a.id,
        code=a.code,
        title=a.title,
        category=a.category,
        competency_id=a.competency_id,
        competency_name=comp_name,
        description=a.description,
        total_questions=len(q_responses),
        passing_score=a.passing_score,
        time_limit_minutes=a.time_limit_minutes,
        difficulty=a.difficulty,
        is_active=a.is_active,
        questions=q_responses
    )

@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
def submit_assessment(
    assessment_id: int,
    payload: AssessmentSubmitRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = CompetencyService(db)
    user_answers = {ans.question_id: ans.selected_option for ans in payload.answers}

    try:
        result = service.evaluate_assessment(
            employee_id=payload.employee_id.upper(),
            assessment_id=assessment_id,
            user_answers=user_answers
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
