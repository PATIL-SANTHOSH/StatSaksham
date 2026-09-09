import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.database.session import get_db
from app.core.config import settings
from app.models.quiz import QuizDocument, QuizChunk, QuizQuestion, QuizAttempt, QuizAnswer
from app.models.competency import Competency, EmployeeCompetency
from app.schemas.quiz import (
    QuizDocumentResponse,
    QuizQuestionResponse,
    QuizGenerateRequest,
    QuizSubmitRequest,
    QuizResultResponse,
    QuizFeedbackItem
)
from app.ai.rag_engine import rag_engine
from app.ai.quiz_generator import QuizGenerator
from app.api.deps import get_current_user

router = APIRouter(prefix="/quiz", tags=["AI Quiz & RAG Generator"])

@router.post("/upload", response_model=QuizDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    employee_id: str = Form("OSS1001"),
    competency_tag: str = Form("General Statistics"),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    filename = file.filename or "uploaded_doc.txt"
    file_ext = os.path.splitext(filename)[1].lower()
    
    # Save file
    saved_filename = f"{employee_id}_{int(datetime.now().timestamp())}_{filename}"
    file_path = os.path.join(upload_dir, saved_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size_kb = round(os.path.getsize(file_path) / 1024.0, 2)
    doc_title = title if title else os.path.splitext(filename)[0]

    # Extract and chunk text via RAGEngine
    raw_text = rag_engine.extract_text(file_path, file_ext)
    chunks_data = rag_engine.chunk_text(raw_text, chunk_size=600, overlap=100)

    # Save QuizDocument
    doc = QuizDocument(
        filename=filename,
        file_type=file_ext.replace(".", "").upper(),
        file_path=file_path,
        file_size_kb=file_size_kb,
        uploaded_by=employee_id.upper(),
        competency_tag=competency_tag,
        title=doc_title,
        chunk_count=len(chunks_data),
        uploaded_at=datetime.now(timezone.utc)
    )
    db.add(doc)
    db.flush()

    # Save Chunks with embeddings
    for c in chunks_data:
        emb = rag_engine.compute_embedding(c["content"])
        chunk_obj = QuizChunk(
            document_id=doc.id,
            chunk_index=c["chunk_index"],
            content=c["content"],
            token_count=c["token_count"],
            embedding_json=emb
        )
        db.add(chunk_obj)

    db.commit()
    db.refresh(doc)
    return doc

@router.get("/documents/{employee_id}", response_model=List[QuizDocumentResponse])
def list_user_documents(employee_id: str, db: Session = Depends(get_db)):
    docs = db.query(QuizDocument).filter(
        QuizDocument.uploaded_by == employee_id.upper()
    ).order_by(QuizDocument.uploaded_at.desc()).all()
    return docs

@router.post("/generate", response_model=List[QuizQuestionResponse])
def generate_quiz(
    payload: QuizGenerateRequest,
    db: Session = Depends(get_db)
):
    generator = QuizGenerator(db)
    
    # If raw text provided without document_id, create temporary document
    doc_id = payload.document_id
    if not doc_id:
        if not payload.raw_text or len(payload.raw_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Either document_id or raw_text must be provided")
        
        # Create lightweight document
        chunks_data = rag_engine.chunk_text(payload.raw_text, chunk_size=600, overlap=100)
        temp_doc = QuizDocument(
            filename="Manual_Text_Extract.txt",
            file_type="TXT",
            file_path="memory://manual",
            file_size_kb=len(payload.raw_text) / 1024.0,
            uploaded_by="OSS1001",
            competency_tag=payload.competency,
            title=f"Manual Excerpt: {payload.competency}",
            chunk_count=len(chunks_data),
            uploaded_at=datetime.now(timezone.utc)
        )
        db.add(temp_doc)
        db.flush()

        for c in chunks_data:
            emb = rag_engine.compute_embedding(c["content"])
            db.add(QuizChunk(
                document_id=temp_doc.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                token_count=c["token_count"],
                embedding_json=emb
            ))
        db.commit()
        db.refresh(temp_doc)
        doc_id = temp_doc.id

    try:
        questions = generator.generate_quiz_from_document(
            document_id=doc_id,
            competency=payload.competency,
            difficulty=payload.difficulty,
            num_questions=payload.num_questions
        )
        return questions
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/submit", response_model=QuizResultResponse)
def submit_quiz_attempt(
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db)
):
    emp_id = payload.employee_id.upper()
    total = len(payload.answers)
    if total == 0:
        raise HTTPException(status_code=400, detail="No answers submitted")

    correct_count = 0
    feedback_items = []
    question_ids = [a.question_id for a in payload.answers]
    db_questions = {
        q.id: q for q in db.query(QuizQuestion).filter(QuizQuestion.id.in_(question_ids)).all()
    }

    difficulty = "Intermediate"
    for ans in payload.answers:
        q = db_questions.get(ans.question_id)
        if not q:
            continue
        difficulty = q.difficulty
        user_choice = ans.selected_option.upper().strip()
        is_corr = (user_choice == q.correct_option.upper().strip())
        if is_corr:
            correct_count += 1

        feedback_items.append(QuizFeedbackItem(
            question_id=q.id,
            question_text=q.question_text,
            selected_option=user_choice,
            correct_option=q.correct_option,
            is_correct=is_corr,
            explanation=q.explanation,
            source_reference=q.source_reference
        ))

    score_pct = round((correct_count / max(1, total)) * 100.0, 1)
    passed = score_pct >= 60.0

    # Competency update logic
    comp_updated = False
    new_lvl = None
    if passed:
        # Match competency
        comp = db.query(Competency).filter(Competency.name.ilike(f"%{payload.competency}%")).first()
        if comp:
            ec = db.query(EmployeeCompetency).filter(
                EmployeeCompetency.employee_id == emp_id,
                EmployeeCompetency.competency_id == comp.id
            ).first()
            
            if ec:
                prev_lvl = ec.current_level
                if score_pct >= 80.0:
                    ec.current_level = min(5, prev_lvl + 1)
                ec.assessed_level = ec.current_level
                ec.last_assessed_date = datetime.now(timezone.utc)
                ec.verified_by_assessment = True
                ec.source = "AI Document Quiz"
                comp_updated = (ec.current_level > prev_lvl)
                new_lvl = ec.current_level
            else:
                ec = EmployeeCompetency(
                    employee_id=emp_id,
                    competency_id=comp.id,
                    current_level=3 if score_pct >= 80.0 else 2,
                    assessed_level=3 if score_pct >= 80.0 else 2,
                    verified_by_assessment=True,
                    source="AI Document Quiz"
                )
                db.add(ec)
                comp_updated = True
                new_lvl = ec.current_level

    # Record attempt
    attempt = QuizAttempt(
        employee_id=emp_id,
        document_id=payload.document_id,
        competency=payload.competency,
        difficulty=difficulty,
        total_questions=total,
        correct_count=correct_count,
        score_percentage=score_pct,
        competency_gain_awarded=comp_updated,
        attempted_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    db.flush()

    for ans in payload.answers:
        q = db_questions.get(ans.question_id)
        if q:
            is_corr = (ans.selected_option.upper().strip() == q.correct_option.upper().strip())
            db.add(QuizAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option=ans.selected_option.upper().strip(),
                is_correct=is_corr
            ))

    db.commit()
    db.refresh(attempt)

    return QuizResultResponse(
        attempt_id=attempt.id,
        employee_id=emp_id,
        competency=payload.competency,
        difficulty=difficulty,
        total_questions=total,
        correct_count=correct_count,
        score_percentage=score_pct,
        passed=passed,
        competency_updated=comp_updated,
        new_competency_level=new_lvl,
        feedback=feedback_items,
        attempted_at=attempt.attempted_at
    )
