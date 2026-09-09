from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base

class QuizDocument(Base):
    __tablename__ = "quiz_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # PDF, PPTX, TXT, DOCX
    file_path = Column(String(500), nullable=False)
    file_size_kb = Column(Float, default=0.0)
    uploaded_by = Column(String(50), nullable=False)
    competency_tag = Column(String(100), default="General Statistics")
    title = Column(String(255), nullable=False)
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    chunks = relationship("QuizChunk", back_populates="document", cascade="all, delete-orphan")
    questions = relationship("QuizQuestion", back_populates="document", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="document", cascade="all, delete-orphan")

class QuizChunk(Base):
    __tablename__ = "quiz_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("quiz_documents.id"), index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding_json = Column(JSON, nullable=True)  # List of floats for vector embedding

    # Relationships
    document = relationship("QuizDocument", back_populates="chunks")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("quiz_documents.id"), index=True, nullable=False)
    chunk_id = Column(Integer, ForeignKey("quiz_chunks.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(String(1), nullable=False)  # A, B, C, D
    explanation = Column(Text, nullable=True)
    competency = Column(String(100), default="General Statistics")
    difficulty = Column(String(20), default="Intermediate")
    source_reference = Column(String(255), nullable=True)

    # Relationships
    document = relationship("QuizDocument", back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), index=True, nullable=False)
    document_id = Column(Integer, ForeignKey("quiz_documents.id"), nullable=True)
    competency = Column(String(100), nullable=False)
    difficulty = Column(String(20), default="Intermediate")
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)
    competency_gain_awarded = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    employee = relationship("Employee", back_populates="quiz_attempts")
    document = relationship("QuizDocument", back_populates="attempts")
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete-orphan")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), index=True, nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    selected_option = Column(String(1), nullable=False)
    is_correct = Column(Boolean, nullable=False)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="answers")
    question = relationship("QuizQuestion")
