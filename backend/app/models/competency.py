from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class Competency(Base):
    __tablename__ = "competencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # Statistical, Technical, Digital Governance, Behavioural / Managerial
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    max_level = Column(Integer, default=5)

    # Relationships
    requirements = relationship("CompetencyRequirement", back_populates="competency", cascade="all, delete-orphan")
    employee_competencies = relationship("EmployeeCompetency", back_populates="competency", cascade="all, delete-orphan")

class CompetencyRequirement(Base):
    __tablename__ = "competency_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_role = Column(String(100), index=True, nullable=False)
    department_code = Column(String(50), index=True, nullable=True)
    competency_id = Column(Integer, ForeignKey("competencies.id"), nullable=False)
    required_level = Column(Integer, nullable=False, default=3)  # 1 to 5
    priority_weight = Column(Integer, default=3)  # 1 (low) to 5 (critical)
    rationale = Column(Text, nullable=True)

    # Relationships
    competency = relationship("Competency", back_populates="requirements")

    __table_args__ = (
        UniqueConstraint('job_role', 'competency_id', name='uq_job_role_competency'),
    )

class EmployeeCompetency(Base):
    __tablename__ = "employee_competencies"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), index=True, nullable=False)
    competency_id = Column(Integer, ForeignKey("competencies.id"), nullable=False)
    current_level = Column(Integer, default=1, nullable=False)  # 1 to 5
    assessed_level = Column(Integer, default=1)
    last_assessed_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    verified_by_assessment = Column(Boolean, default=False)
    source = Column(String(50), default="Initial Profile")  # Initial Profile, Assessment, Course Completion, AI Quiz

    # Relationships
    employee = relationship("Employee", back_populates="competencies")
    competency = relationship("Competency", back_populates="employee_competencies")

    __table_args__ = (
        UniqueConstraint('employee_id', 'competency_id', name='uq_employee_competency'),
    )
