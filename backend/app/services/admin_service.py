from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.employee import Employee
from app.models.competency import Competency, CompetencyRequirement, EmployeeCompetency
from app.models.progress import LearningProgress
from app.models.recommendation import Recommendation
from app.models.assessment import AssessmentResult
from app.schemas.admin import (
    WorkforceAnalyticsResponse,
    CompetencyDistributionItem,
    DepartmentSkillGapItem,
    TopSkillGapMetric,
    LearningProgressMetric
)

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def get_workforce_analytics(self) -> WorkforceAnalyticsResponse:
        # Total and active employees
        total_employees = self.db.query(Employee).count()
        active_employees = total_employees

        # All employees and their competencies vs requirements
        employees = self.db.query(Employee).all()
        competencies = self.db.query(Competency).all()
        comp_dict = {c.id: c for c in competencies}

        # Role requirements lookup: (job_role, comp_id) -> req
        requirements = self.db.query(CompetencyRequirement).all()
        req_map: Dict[str, Dict[int, CompetencyRequirement]] = {}
        for r in requirements:
            req_map.setdefault(r.job_role, {})[r.competency_id] = r

        # Employee competencies lookup: emp_id -> {comp_id: level}
        emp_comps = self.db.query(EmployeeCompetency).all()
        emp_comp_map: Dict[str, Dict[int, int]] = {}
        for ec in emp_comps:
            emp_comp_map.setdefault(ec.employee_id, {})[ec.competency_id] = ec.current_level

        # Calculate workforce gaps
        employees_with_gaps = 0
        total_skill_gaps = 0
        high_priority_gaps_count = 0
        gap_by_competency: Dict[int, List[int]] = {}
        dept_stats: Dict[str, Dict[str, Any]] = {}

        for emp in employees:
            emp_has_gap = False
            emp_gaps_list = []
            role_reqs = req_map.get(emp.job_role, {})
            current_levels = emp_comp_map.get(emp.employee_id, {})

            dept_name = emp.department
            dept_code = emp.department_code or dept_name[:4].upper()
            if dept_name not in dept_stats:
                dept_stats[dept_name] = {
                    "department": dept_name,
                    "department_code": dept_code,
                    "employee_count": 0,
                    "employees_with_gaps": 0,
                    "total_gap_sum": 0,
                    "high_priority_gaps": 0,
                    "gap_counts_by_comp": {}
                }
            dept_stats[dept_name]["employee_count"] += 1

            for comp_id, req in role_reqs.items():
                curr = current_levels.get(comp_id, 1)
                req_lvl = req.required_level
                gap = max(0, req_lvl - curr)
                if gap > 0:
                    emp_has_gap = True
                    total_skill_gaps += 1
                    gap_by_competency.setdefault(comp_id, []).append(gap)
                    emp_gaps_list.append(gap)
                    dept_stats[dept_name]["total_gap_sum"] += gap
                    
                    if gap >= 2 or req.priority_weight >= 4:
                        high_priority_gaps_count += 1
                        dept_stats[dept_name]["high_priority_gaps"] += 1

                    c_name = comp_dict.get(comp_id).name if comp_id in comp_dict else "Unknown"
                    dept_stats[dept_name]["gap_counts_by_comp"][c_name] = (
                        dept_stats[dept_name]["gap_counts_by_comp"].get(c_name, 0) + 1
                    )

            if emp_has_gap:
                employees_with_gaps += 1
                dept_stats[dept_name]["employees_with_gaps"] += 1

        # Build Top Skill Gaps metric
        top_skill_gaps: List[TopSkillGapMetric] = []
        for comp_id, gaps in gap_by_competency.items():
            if comp_id in comp_dict:
                c = comp_dict[comp_id]
                avg_g = round(sum(gaps) / len(gaps), 2)
                prio = "High" if avg_g >= 1.8 or len(gaps) >= 15 else "Medium"
                top_skill_gaps.append(TopSkillGapMetric(
                    competency_name=c.name,
                    category=c.category,
                    affected_employees_count=len(gaps),
                    average_gap=avg_g,
                    priority=prio
                ))
        top_skill_gaps.sort(key=lambda x: (x.affected_employees_count, x.average_gap), reverse=True)

        # Build Department Summaries
        department_summaries: List[DepartmentSkillGapItem] = []
        for dept_name, d in dept_stats.items():
            top_comps = sorted(d["gap_counts_by_comp"].items(), key=lambda x: x[1], reverse=True)
            top_3 = [c[0] for c in top_comps[:3]]
            avg_g = round(d["total_gap_sum"] / max(1, d["employee_count"]), 2)
            department_summaries.append(DepartmentSkillGapItem(
                department=dept_name,
                department_code=d["department_code"],
                employee_count=d["employee_count"],
                employees_with_gaps=d["employees_with_gaps"],
                average_gap=avg_g,
                high_priority_gaps=d["high_priority_gaps"],
                top_gap_competencies=top_3
            ))

        # Build Competency Distribution
        competency_distributions: List[CompetencyDistributionItem] = []
        for comp in competencies:
            levels = [
                emp_comp_map.get(emp.employee_id, {}).get(comp.id, 1)
                for emp in employees
            ]
            if levels:
                b_cnt = sum(1 for l in levels if l <= 2)
                i_cnt = sum(1 for l in levels if l == 3)
                a_cnt = sum(1 for l in levels if l >= 4)
                avg_l = round(sum(levels) / len(levels), 2)
                competency_distributions.append(CompetencyDistributionItem(
                    competency_name=comp.name,
                    category=comp.category,
                    beginner_count=b_cnt,
                    intermediate_count=i_cnt,
                    advanced_count=a_cnt,
                    average_level=avg_l
                ))

        # Learning Progress Metrics
        enrollments = self.db.query(LearningProgress).all()
        igot_enrolled = [p for p in enrollments if p.course_type == "iGOT"]
        nssta_enrolled = [p for p in enrollments if p.course_type == "NSSTA"]

        learning_progress_metrics = [
            LearningProgressMetric(
                course_type="iGOT Karmayogi",
                total_enrollments=len(igot_enrolled),
                completed_count=sum(1 for p in igot_enrolled if p.status == "Completed"),
                in_progress_count=sum(1 for p in igot_enrolled if p.status == "In Progress"),
                completion_rate_percentage=round(
                    (sum(1 for p in igot_enrolled if p.status == "Completed") / max(1, len(igot_enrolled))) * 100.0, 1
                )
            ),
            LearningProgressMetric(
                course_type="NSSTA / TPAC",
                total_enrollments=len(nssta_enrolled),
                completed_count=sum(1 for p in nssta_enrolled if p.status == "Completed"),
                in_progress_count=sum(1 for p in nssta_enrolled if p.status == "In Progress"),
                completion_rate_percentage=round(
                    (sum(1 for p in nssta_enrolled if p.status == "Completed") / max(1, len(nssta_enrolled))) * 100.0, 1
                )
            )
        ]

        total_recommended = self.db.query(Recommendation).count()
        total_enrolled = len(enrollments)
        total_completed = sum(1 for p in enrollments if p.status == "Completed")

        # Average competency improvement from assessment results
        assessment_results = self.db.query(AssessmentResult).all()
        improvements = [r.new_level - r.previous_level for r in assessment_results if r.new_level > r.previous_level]
        avg_improvement = round(sum(improvements) / max(1, len(improvements)), 2) if improvements else 0.85

        # Workforce readiness score (0-100)
        readiness_score = round(
            max(40.0, 100.0 - (total_skill_gaps / max(1, total_employees * 4) * 50.0)), 1
        )

        return WorkforceAnalyticsResponse(
            total_employees=total_employees,
            active_employees=active_employees,
            employees_with_skill_gaps=employees_with_gaps,
            total_skill_gaps_identified=total_skill_gaps,
            high_priority_gaps_count=high_priority_gaps_count,
            courses_recommended_count=total_recommended,
            courses_enrolled_count=total_enrolled,
            courses_completed_count=total_completed,
            average_competency_improvement=avg_improvement,
            workforce_readiness_score=readiness_score,
            top_skill_gaps=top_skill_gaps[:10],
            department_summaries=department_summaries,
            competency_distributions=competency_distributions[:12],
            learning_progress_metrics=learning_progress_metrics
        )
