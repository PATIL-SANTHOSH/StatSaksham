from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), index=True, nullable=False)
    course_type = Column(String(20), nullable=False)  # "iGOT" or "NSSTA"
    course_id = Column(String(50), nullable=False)    # igot course_id or nssta training_id
    title = Column(String(200), nullable=False)
    provider = Column(String(100), nullable=False)
    competency_name = Column(String(100), nullable=False)
    priority = Column(String(20), default="Medium")   # High, Medium, Low
    relevance_score = Column(Float, default=85.0)
    relevance_label = Column(String(50), default="Highly Relevant")  # Highly Relevant, Relevant, Moderately Relevant
    reason = Column(Text, nullable=False)
    estimated_duration = Column(String(50), default="4 Hours")
    expected_competency_improvement = Column(String(100), default="+1 Level")
    status = Column(String(30), default="Recommended") # Recommended, Enrolled, In Progress, Completed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    employee = relationship("Employee", back_populates="recommendations")
