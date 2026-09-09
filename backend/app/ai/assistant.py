from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.employee import Employee
from app.models.ai_conversation import AIConversation, AIMessage
from app.models.quiz import QuizDocument, QuizChunk
from app.ai.ollama_client import ollama_client
from app.ai.rag_engine import rag_engine
from app.ai.fallback_ai import fallback_ai
from app.schemas.ai import ChatResponse

class LearningAssistantService:
    def __init__(self, db: Session):
        self.db = db

    def chat(
        self,
        employee_id: str,
        message: str,
        conversation_id: Optional[int] = None,
        document_id: Optional[int] = None,
        context_competency: Optional[str] = None
    ) -> ChatResponse:
        emp = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
        emp_name = emp.name if emp else "Officer"
        job_role = emp.job_role if emp else "Statistical Official"
        dept = emp.department if emp else "MoSPI"
        assignment = emp.current_assignment if emp else "Statistical Operations"

        # Manage conversation session
        if conversation_id:
            conv = self.db.query(AIConversation).filter(
                AIConversation.id == conversation_id,
                AIConversation.employee_id == employee_id
            ).first()
        else:
            conv = None

        if not conv:
            conv = AIConversation(
                employee_id=employee_id,
                title=f"{message[:40]}..." if len(message) > 40 else message
            )
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)

        # Save user message
        user_msg = AIMessage(
            conversation_id=conv.id,
            role="user",
            content=message
        )
        self.db.add(user_msg)
        self.db.commit()

        # Document context lookup for RAG
        doc_context = ""
        sources = []
        if document_id:
            doc = self.db.query(QuizDocument).filter(QuizDocument.id == document_id).first()
            if doc:
                chunks = self.db.query(QuizChunk).filter(QuizChunk.document_id == document_id).all()
                chunk_dicts = [{"content": c.content, "chunk_index": c.chunk_index} for c in chunks]
                top_chunks = rag_engine.similarity_search(message, chunk_dicts, top_k=3)
                doc_context = "\n\n".join([f"Excerpt: {c['content']}" for c in top_chunks])
                sources.append(f"Document: {doc.filename}")

        # Attempt Ollama LLM response
        assistant_reply = None
        model_used = None

        if ollama_client.is_available():
            active_model = ollama_client.get_active_model()
            system_prompt = (
                f"You are StatSaksham AI, an intelligent mentor for officers in India's Official Statistical System (MoSPI).\n"
                f"Officer: {emp_name}, {job_role} at {dept}. Assignment: {assignment}.\n"
                f"Provide concise, structured guidance grounded in Indian statistical methodologies "
                f"(SNA 2008, NSS Survey Design, CPI/IIP, SDG Framework, Python/R, and iGOT Karmayogi capacity building)."
            )

            context_block = ""
            if doc_context:
                context_block = f"\n\nDOCUMENT CONTEXT:\n{doc_context}\n"
            if context_competency:
                context_block += f"\nFOCUS COMPETENCY: {context_competency}\n"

            prompt = f"{context_block}\nOfficer's Question:\n{message}"
            llm_res = ollama_client.generate(prompt, system=system_prompt, model=active_model)
            if llm_res and len(llm_res.strip()) > 10:
                assistant_reply = llm_res.strip()
                model_used = f"Ollama ({active_model})"

        # Fallback if Ollama is not running, times out, or returns empty
        if not assistant_reply:
            fb = fallback_ai.get_assistant_response(
                user_message=message,
                employee_name=emp_name,
                job_role=job_role,
                document_context=doc_context
            )
            assistant_reply = fb["message"]
            sources.extend(fb["sources"])
            model_used = fb["model_used"]

        # Save assistant message
        ast_msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content=assistant_reply,
            sources_json={"sources": sources}
        )
        self.db.add(ast_msg)
        conv.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return ChatResponse(
            conversation_id=conv.id,
            message=assistant_reply,
            role="assistant",
            sources=list(set(sources)),
            model_used=model_used,
            created_at=ast_msg.created_at
        )
