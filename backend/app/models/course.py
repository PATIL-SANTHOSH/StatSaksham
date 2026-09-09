from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from datetime import datetime, timezone
from app.database.session import Base

class IGOTCourse(Base):
    __tablename__ = "igot_courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), default="iGOT Karmayogi / DoPT")
    description = Column(Text, nullable=True)
    duration_hours = Column(Float, default=2.0)
    competency_tags = Column(String(255), nullable=False)  # comma-separated e.g. "Python, Data Analysis, SQL"
    category = Column(String(50), default="Technical")
    difficulty = Column(String(20), default="Intermediate")  # Beginner, Intermediate, Advanced
    language = Column(String(50), default="English / Hindi")
    course_url = Column(String(255), nullable=True)
    source = Column(String(50), default="iGOT Karmayogi Prototype Catalogue")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class NSSTAProgramme(Base):
    __tablename__ = "nssta_programmes"

    id = Column(Integer, primary_key=True, index=True)
    training_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), default="NSSTA Greater Noida / MoSPI")
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, default=5)
    duration_hours = Column(Float, default=30.0)
    competency_tags = Column(String(255), nullable=False)  # comma-separated e.g. "National Accounts, Price Statistics"
    category = Column(String(50), default="Statistical")
    level = Column(String(20), default="Advanced")
    target_audience = Column(String(150), default="ISS / SSS Officers")
    programme_url = Column(String(255), nullable=True)
    source = Column(String(50), default="NSSTA / TPAC Prototype Catalogue")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
