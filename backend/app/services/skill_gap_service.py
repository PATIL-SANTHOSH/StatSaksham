from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.competency import Competency, CompetencyRequirement, EmployeeCompetency
from app.schemas.competency import SkillGapItem, SkillGapResponse

class SkillGapService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_skill_gaps(self, employee_id: str) -> SkillGapResponse:
        emp = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")

        # Get role requirements for this employee's job role
        requirements = (
            self.db.query(CompetencyRequirement, Competency)
            .join(Competency, CompetencyRequirement.competency_id == Competency.id)
            .filter(CompetencyRequirement.job_role == emp.job_role)
            .all()
        )

        # If no specific role requirements found, fallback to department/generic matching
        if not requirements:
            requirements = (
                self.db.query(CompetencyRequirement, Competency)
                .join(Competency, CompetencyRequirement.competency_id == Competency.id)
                .filter(CompetencyRequirement.job_role.ilike(f"%{emp.job_role}%"))
                .all()
            )

        # Get current employee competencies
        emp_competencies = {
            ec.competency_id: ec.current_level
            for ec in self.db.query(EmployeeCompetency).filter(EmployeeCompetency.employee_id == employee_id).all()
        }

        gap_items: List[SkillGapItem] = []
        total_gaps = 0
        high_priority_count = 0
        medium_priority_count = 0
        low_priority_count = 0
        sum_gaps = 0.0

        for req, comp in requirements:
            current_level = emp_competencies.get(comp.id, 1)
            required_level = req.required_level
            gap = max(0, required_level - current_level)
            
            # Gap category
            if gap == 0:
                gap_category = "No Gap"
            elif gap == 1:
                gap_category = "Low Gap"
            elif gap == 2:
                gap_category = "Medium Gap"
            else:
                gap_category = "High Gap"

            # Check if assignment directly mentions this competency
            assignment_match = (
                comp.name.lower() in emp.current_assignment.lower() or
                comp.category.lower() in emp.current_assignment.lower()
            )

            # Priority calculation: gap * priority_weight + assignment_bonus
            priority_score = (gap * 2.0) + (req.priority_weight * 1.5) + (3.0 if assignment_match else 0.0)
            
            if gap == 0:
                priority = "None"
            elif gap >= 2 or priority_score >= 8.0:
                priority = "High"
                high_priority_count += 1
            elif gap == 1 and priority_score >= 5.0:
                priority = "Medium"
                medium_priority_count += 1
            else:
                priority = "Low"
                low_priority_count += 1

            if gap > 0:
                total_gaps += 1
                sum_gaps += gap

            # Human-readable rationale
            if gap > 0:
                assignment_note = f" Critical for your current assignment in '{emp.current_assignment}'." if assignment_match else ""
                reason = (
                    f"Your current {comp.name} competency is level {current_level}/5, while your role as "
                    f"'{emp.job_role}' requires level {required_level}/5 (Gap: {gap}).{assignment_note}"
                )
                recommended_action = f"Complete targeted iGOT / NSSTA modules in {comp.name} to bridge {gap} level(s)."
            else:
                reason = f"Your current competency ({current_level}/5) fully meets the required benchmark ({required_level}/5) for your role."
                recommended_action = "Maintain mastery through periodic refresher assessments."

            gap_items.append(SkillGapItem(
                competency_id=comp.id,
                competency_code=comp.code,
                competency_name=comp.name,
                category=comp.category,
                current_level=current_level,
                required_level=required_level,
                gap=gap,
                gap_category=gap_category,
                priority=priority,
                priority_score=round(priority_score, 1),
                importance_weight=req.priority_weight,
                reason=reason,
                recommended_action=recommended_action
            ))

        # Sort gap items by priority (High -> Medium -> Low -> None) then gap size descending
        priority_order = {"High": 3, "Medium": 2, "Low": 1, "None": 0}
        gap_items.sort(key=lambda x: (priority_order.get(x.priority, 0), x.gap, x.priority_score), reverse=True)

        total_competencies = len(gap_items)
        avg_gap = round(sum_gaps / total_competencies, 2) if total_competencies > 0 else 0.0

        # Readiness percentage: (Sum of current levels / Sum of required levels) * 100
        sum_current = sum(g.current_level for g in gap_items)
        sum_required = sum(g.required_level for g in gap_items)
        readiness_pct = round((sum_current / sum_required * 100.0), 1) if sum_required > 0 else 100.0

        return SkillGapResponse(
            employee_id=emp.employee_id,
            employee_name=emp.name,
            job_role=emp.job_role,
            department=emp.department,
            current_assignment=emp.current_assignment,
            total_competencies=total_competencies,
            total_gaps=total_gaps,
            high_priority_gaps_count=high_priority_count,
            medium_priority_gaps_count=medium_priority_count,
            low_priority_gaps_count=low_priority_count,
            average_gap=avg_gap,
            overall_readiness_percentage=min(100.0, readiness_pct),
            gaps=gap_items
        )
