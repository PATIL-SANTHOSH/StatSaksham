from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), index=True, nullable=False)
    course_type = Column(String(20), nullable=False)  # "iGOT" or "NSSTA"
    course_id = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), nullable=False)
    status = Column(String(30), default="Enrolled")  # Enrolled, In Progress, Completed
    progress_percentage = Column(Float, default=0.0)
    hours_spent = Column(Float, default=0.0)
    competency_name = Column(String(100), nullable=True)
    competency_gain_applied = Column(Boolean, default=False)
    enrolled_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    employee = relationship("Employee", back_populates="progress_records")
