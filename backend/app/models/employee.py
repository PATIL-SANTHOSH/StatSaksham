from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    department = Column(String(150), nullable=False)
    department_code = Column(String(50), nullable=True)
    designation = Column(String(100), nullable=False)
    job_role = Column(String(100), nullable=False)
    current_assignment = Column(String(200), nullable=False)
    education = Column(String(150), nullable=False)
    years_of_experience = Column(Float, default=0.0)
    joining_date = Column(Date, nullable=True)
    previous_trainings = Column(Text, nullable=True)
    competency_domain = Column(String(100), default="Statistical")
    role = Column(String(20), default="LEARNER")  # LEARNER or ADMIN
    profile_photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    competencies = relationship("EmployeeCompetency", back_populates="employee", cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="employee", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="employee", cascade="all, delete-orphan")
    progress_records = relationship("LearningProgress", back_populates="employee", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="employee", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="employee", cascade="all, delete-orphan")
