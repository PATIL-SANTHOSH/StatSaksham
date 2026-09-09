from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.competency import Competency, CompetencyRequirement, EmployeeCompetency
from app.models.employee import Employee
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResult
from app.schemas.assessment import AssessmentResultResponse, QuestionFeedback

class CompetencyService:
    def __init__(self, db: Session):
        self.db = db

    def get_employee_competencies(self, employee_id: str) -> List[Dict[str, Any]]:
        records = (
            self.db.query(EmployeeCompetency, Competency)
            .join(Competency, EmployeeCompetency.competency_id == Competency.id)
            .filter(EmployeeCompetency.employee_id == employee_id)
            .all()
        )
        results = []
        for emp_comp, comp in records:
            results.append({
                "id": emp_comp.id,
                "employee_id": emp_comp.employee_id,
                "competency_id": comp.id,
                "competency_code": comp.code,
                "competency_name": comp.name,
                "category": comp.category,
                "domain": comp.domain,
                "description": comp.description,
                "current_level": emp_comp.current_level,
                "assessed_level": emp_comp.assessed_level,
                "last_assessed_date": emp_comp.last_assessed_date,
                "verified_by_assessment": emp_comp.verified_by_assessment,
                "source": emp_comp.source
            })
        return results

    def evaluate_assessment(self, employee_id: str, assessment_id: int, user_answers: Dict[int, str]) -> AssessmentResultResponse:
        assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        questions = self.db.query(AssessmentQuestion).filter(AssessmentQuestion.assessment_id == assessment_id).all()
        total_questions = len(questions)
        if total_questions == 0:
            raise ValueError("No questions found in this assessment")

        correct_count = 0
        feedback_list = []

        for q in questions:
            selected = user_answers.get(q.id, "").upper().strip()
            is_correct = (selected == q.correct_option.upper().strip())
            if is_correct:
                correct_count += 1
            
            feedback_list.append(QuestionFeedback(
                question_id=q.id,
                question_text=q.question_text,
                selected_option=selected or "None",
                correct_option=q.correct_option,
                is_correct=is_correct,
                explanation=q.explanation
            ))

        score_percentage = (correct_count / total_questions) * 100.0
        passed = score_percentage >= assessment.passing_score

        # Determine competency improvement
        # Find corresponding employee competency
        emp_comp = None
        if assessment.competency_id:
            emp_comp = self.db.query(EmployeeCompetency).filter(
                EmployeeCompetency.employee_id == employee_id,
                EmployeeCompetency.competency_id == assessment.competency_id
            ).first()

        previous_level = emp_comp.current_level if emp_comp else 1
        new_level = previous_level

        if passed:
            # High score: 80%+ -> advance by 1 level up to max 5; 100% -> advance by up to 2 levels
            if score_percentage >= 90:
                new_level = min(5, previous_level + 2 if assessment.difficulty == "Advanced" else previous_level + 1)
            elif score_percentage >= 70:
                new_level = min(5, previous_level + 1)
            
            if emp_comp:
                emp_comp.current_level = new_level
                emp_comp.assessed_level = new_level
                emp_comp.last_assessed_date = datetime.now(timezone.utc)
                emp_comp.verified_by_assessment = True
                emp_comp.source = "Competency Assessment"

        # Record assessment result
        result = AssessmentResult(
            employee_id=employee_id,
            assessment_id=assessment_id,
            score_percentage=score_percentage,
            total_questions=total_questions,
            correct_count=correct_count,
            previous_level=previous_level,
            new_level=new_level,
            completed_at=datetime.now(timezone.utc),
            answers_json={"answers": [f.dict() for f in feedback_list]}
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)

        comp_name = assessment.title
        if assessment.competency_id:
            c = self.db.query(Competency).filter(Competency.id == assessment.competency_id).first()
            if c:
                comp_name = c.name

        return AssessmentResultResponse(
            result_id=result.id,
            employee_id=employee_id,
            assessment_id=assessment.id,
            assessment_title=assessment.title,
            competency_name=comp_name,
            total_questions=total_questions,
            correct_count=correct_count,
            score_percentage=round(score_percentage, 1),
            passed=passed,
            previous_level=previous_level,
            new_level=new_level,
            level_improved=(new_level > previous_level),
            feedback=feedback_list,
            completed_at=result.completed_at
        )
