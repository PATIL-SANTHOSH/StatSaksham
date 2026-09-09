from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # Statistical, Technical, Digital Governance, Behavioural / Managerial
    competency_id = Column(Integer, ForeignKey("competencies.id"), nullable=True)
    description = Column(Text, nullable=True)
    total_questions = Column(Integer, default=5)
    passing_score = Column(Float, default=60.0)  # percentage
    time_limit_minutes = Column(Integer, default=15)
    difficulty = Column(String(20), default="Intermediate")  # Beginner, Intermediate, Advanced
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), index=True, nullable=False)
    competency_id = Column(Integer, ForeignKey("competencies.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(1), nullable=False)  # 'A', 'B', 'C', 'D'
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="Intermediate")

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")

class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), index=True, nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    score_percentage = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    previous_level = Column(Integer, nullable=False)
    new_level = Column(Integer, nullable=False)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    answers_json = Column(JSON, nullable=True)

    # Relationships
    employee = relationship("Employee", back_populates="assessment_results")
    assessment = relationship("Assessment", back_populates="results")
