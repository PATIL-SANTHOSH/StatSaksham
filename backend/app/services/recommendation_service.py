from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.employee import Employee
from app.models.recommendation import Recommendation
from app.models.progress import LearningProgress
from app.services.skill_gap_service import SkillGapService
from app.integrations.igot_adapter import IGOTAdapter
from app.integrations.nssta_adapter import NSSTAAdapter
from app.integrations.base import StandardCourseItem
from app.schemas.recommendation import RecommendationResponse, RecommendationListResponse

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.skill_gap_service = SkillGapService(db)
        self.igot_adapter = IGOTAdapter(db)
        self.nssta_adapter = NSSTAAdapter(db)

    def generate_recommendations(self, employee_id: str, force_refresh: bool = False) -> RecommendationListResponse:
        emp = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")

        # Check existing recommendations unless force_refresh
        if not force_refresh:
            existing = self.db.query(Recommendation).filter(Recommendation.employee_id == employee_id).all()
            if existing and len(existing) >= 4:
                return self._format_response(employee_id, existing)

        # Clear existing un-enrolled recommendations for a fresh recalculation
        self.db.query(Recommendation).filter(
            Recommendation.employee_id == employee_id,
            Recommendation.status == "Recommended"
        ).delete()
        self.db.commit()

        # 1. Fetch skill gaps
        gap_report = self.skill_gap_service.calculate_skill_gaps(employee_id)
        active_gaps = [g for g in gap_report.gaps if g.gap > 0]

        # 2. Fetch enrolled/completed courses to avoid recommending already done courses
        completed_ids = {
            p.course_id for p in self.db.query(LearningProgress).filter(
                LearningProgress.employee_id == employee_id,
                LearningProgress.status.in_(["Completed", "In Progress"])
            ).all()
        }

        # 3. Retrieve courses from iGOT and NSSTA adapters
        igot_courses = self.igot_adapter.search_courses(limit=50)
        nssta_courses = self.nssta_adapter.search_courses(limit=50)
        all_catalog_courses: List[StandardCourseItem] = igot_courses + nssta_courses

        scored_recommendations = []

        for course in all_catalog_courses:
            if course.id in completed_ids:
                continue

            course_tags = [t.lower() for t in course.competency_tags]
            
            # Match against active gaps
            matched_gap = None
            for gap in active_gaps:
                comp_lower = gap.competency_name.lower()
                if any(comp_lower in tag or tag in comp_lower for tag in course_tags):
                    matched_gap = gap
                    break

            # Base relevance calculation
            relevance_score = 40.0  # baseline
            
            if matched_gap:
                # Big boost based on gap magnitude
                relevance_score += (matched_gap.gap * 15.0)  # +15 to +45
                relevance_score += (matched_gap.importance_weight * 5.0) # +5 to +25
                
                # Boost if mentioned in current assignment
                if matched_gap.competency_name.lower() in emp.current_assignment.lower():
                    relevance_score += 15.0

                # Priority tag
                if matched_gap.gap >= 2 or relevance_score >= 85:
                    priority = "High"
                    relevance_label = "Highly Relevant"
                elif matched_gap.gap == 1 or relevance_score >= 70:
                    priority = "Medium"
                    relevance_label = "Relevant"
                else:
                    priority = "Low"
                    relevance_label = "Moderately Relevant"

                reason = (
                    f"Your current {matched_gap.competency_name} competency is {matched_gap.current_level}/5 while "
                    f"your role as '{emp.job_role}' requires {matched_gap.required_level}/5. "
                    f"This {course.provider_type} course addresses {matched_gap.competency_name} and is targeted to "
                    f"bridge your competency gap of {matched_gap.gap} level(s)."
                )
                competency_name = matched_gap.competency_name
                improvement = f"+{min(2, matched_gap.gap)} Level(s) in {matched_gap.competency_name}"
            else:
                # Check domain / assignment synergy even without direct gap
                assignment_synergy = any(tag in emp.current_assignment.lower() for tag in course_tags)
                prev_training_synergy = any(tag in (emp.previous_trainings or "").lower() for tag in course_tags)
                
                if assignment_synergy:
                    relevance_score += 25.0
                    priority = "Medium"
                    relevance_label = "Relevant"
                    comp_name = course.competency_tags[0] if course.competency_tags else "Statistical Operations"
                    reason = (
                        f"Aligns directly with your current assignment in '{emp.current_assignment}'. "
                        f"Completing this course provides advanced operational expertise."
                    )
                    competency_name = comp_name
                    improvement = f"Strengthen {comp_name}"
                elif prev_training_synergy:
                    relevance_score += 15.0
                    priority = "Low"
                    relevance_label = "Moderately Relevant"
                    comp_name = course.competency_tags[0] if course.competency_tags else "Domain Knowledge"
                    reason = (
                        f"Builds upon your prior background in '{emp.previous_trainings}' to deepen advanced proficiency."
                    )
                    competency_name = comp_name
                    improvement = f"Advanced mastery in {comp_name}"
                else:
                    continue  # Skip un-targeted courses

            relevance_score = min(99.0, max(50.0, relevance_score))

            scored_recommendations.append({
                "employee_id": employee_id,
                "course_type": course.provider_type,
                "course_id": course.id,
                "title": course.title,
                "provider": course.provider,
                "competency_name": competency_name,
                "priority": priority,
                "relevance_score": round(relevance_score, 1),
                "relevance_label": relevance_label,
                "reason": reason,
                "estimated_duration": course.duration_label,
                "expected_competency_improvement": improvement,
                "status": "Recommended"
            })

        # Sort by relevance score descending
        scored_recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Select top recommendations (mix of iGOT and NSSTA)
        top_recs = scored_recommendations[:12]
        
        # Save to database
        db_recs = []
        for rec in top_recs:
            r = Recommendation(
                employee_id=rec["employee_id"],
                course_type=rec["course_type"],
                course_id=rec["course_id"],
                title=rec["title"],
                provider=rec["provider"],
                competency_name=rec["competency_name"],
                priority=rec["priority"],
                relevance_score=rec["relevance_score"],
                relevance_label=rec["relevance_label"],
                reason=rec["reason"],
                estimated_duration=rec["estimated_duration"],
                expected_competency_improvement=rec["expected_competency_improvement"],
                status=rec["status"],
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(r)
            db_recs.append(r)

        self.db.commit()
        for r in db_recs:
            self.db.refresh(r)

        return self._format_response(employee_id, db_recs)

    def _format_response(self, employee_id: str, recs: List[Recommendation]) -> RecommendationListResponse:
        all_recs = [RecommendationResponse.model_validate(r) for r in recs]
        igot_recs = [r for r in all_recs if r.course_type == "iGOT"]
        nssta_recs = [r for r in all_recs if r.course_type == "NSSTA"]
        high_count = sum(1 for r in all_recs if r.priority == "High")

        return RecommendationListResponse(
            employee_id=employee_id,
            total_recommendations=len(all_recs),
            high_priority_count=high_count,
            igot_recommendations=igot_recs,
            nssta_recommendations=nssta_recs,
            all_recommendations=all_recs
        )
