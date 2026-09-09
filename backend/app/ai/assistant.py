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
        doc_filename = None

        if document_id:
            doc = self.db.query(QuizDocument).filter(QuizDocument.id == document_id).first()
            if doc:
                doc_filename = doc.filename
                chunks = self.db.query(QuizChunk).filter(QuizChunk.document_id == document_id).order_by(QuizChunk.chunk_index).all()
                if chunks:
                    chunk_dicts = [
                        {
                            "content": c.content, 
                            "chunk_index": c.chunk_index,
                            "embedding_json": c.embedding_json
                        } 
                        for c in chunks
                    ]
                    top_chunks = rag_engine.similarity_search(message, chunk_dicts, top_k=4)
                    
                    context_pieces = []
                    for c in top_chunks:
                        context_pieces.append(f"[Excerpt {c['chunk_index'] + 1}]:\n{c['content']}")
                        sources.append(f"Document: {doc.filename} (Section {c['chunk_index'] + 1})")
                    
                    doc_context = "\n\n".join(context_pieces)

        # Attempt Ollama LLM response
        assistant_reply = None
        model_used = None

        if ollama_client.is_available():
            active_model = ollama_client.get_active_model()
            
            if doc_context and doc_filename:
                # Grounded RAG System Prompt
                system_prompt = (
                    f"You are the AI Statistical Learning Assistant for India's Ministry of Statistics (MoSPI).\n"
                    f"You are answering a question from {emp_name} ({job_role}, {dept}).\n"
                    f"STRICT INSTRUCTIONS FOR UPLOADED MATERIAL:\n"
                    f"1. Answer the question using ONLY the provided document excerpts from '{doc_filename}'.\n"
                    f"2. Cite the source document clearly in your explanation.\n"
                    f"3. If the provided excerpts do NOT contain enough information to answer the question, explicitly state: "
                    f"'The uploaded material ({doc_filename}) does not contain sufficient information to answer this question.'\n"
                    f"4. Do NOT hallucinate external facts when answering from uploaded material."
                )
                prompt = (
                    f"DOCUMENT EXCERPTS ({doc_filename}):\n\"\"\"\n{doc_context}\n\"\"\"\n\n"
                    f"OFFICER'S QUESTION:\n{message}\n\n"
                    f"GROUNDED ANSWER:"
                )
            else:
                # General Statistical Assistant Prompt
                system_prompt = (
                    f"You are StatSaksham AI, an intelligent capacity-building mentor for officers in India's Official Statistical System (MoSPI).\n"
                    f"Officer: {emp_name}, {job_role} at {dept}. Current Assignment: {assignment}.\n"
                    f"Provide structured, authoritative guidance on Indian statistical methodologies "
                    f"(SNA 2008 National Accounts, NSS Survey & Sampling, CPI/IIP, SDG NIF, Python/R, and iGOT Karmayogi capacity building)."
                )
                context_block = f"\nFOCUS COMPETENCY: {context_competency}\n" if context_competency else ""
                prompt = f"{context_block}\nOfficer's Question:\n{message}"
                sources.append("StatSaksham MoSPI Official Statistical Knowledge Base")

            llm_res = ollama_client.generate(prompt, system=system_prompt, model=active_model, max_tokens=700)
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
            if not sources:
                sources.extend(fb.get("sources", []))
            model_used = fb.get("model_used", "StatSaksham Intelligence Engine")

        # Save assistant message
        unique_sources = list(dict.fromkeys(sources))
        ast_msg = AIMessage(
            conversation_id=conv.id,
            role="assistant",
            content=assistant_reply,
            sources_json={"sources": unique_sources}
        )
        self.db.add(ast_msg)
        conv.updated_at = datetime.now(timezone.utc)
        self.db.commit()

        return ChatResponse(
            conversation_id=conv.id,
            message=assistant_reply,
            role="assistant",
            sources=unique_sources,
            model_used=model_used or "StatSaksham Intelligence Engine",
            created_at=ast_msg.created_at
        )
