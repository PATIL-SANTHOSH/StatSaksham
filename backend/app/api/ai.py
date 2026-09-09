from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database.session import get_db
from app.schemas.ai import ChatRequest, ChatResponse
from app.models.ai_conversation import AIConversation, AIMessage
from app.ai.assistant import LearningAssistantService
from app.ai.ollama_client import ollama_client
from app.api.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["AI Learning Assistant"])

@router.get("/status")
def get_ai_status():
    ollama_ready = ollama_client.is_available()
    active_model = ollama_client.get_active_model() if ollama_ready else "offline"
    return {
        "status": "online" if ollama_ready else "fallback_active",
        "llm_engine": f"Ollama ({active_model})" if ollama_ready else "StatSaksham MoSPI Domain Intelligence Engine (Rule-based Fallback Active)",
        "embedding_engine": "Ollama (nomic-embed-text)" if ollama_ready else "Deterministic Hash Vectorizer",
        "is_ollama_available": ollama_ready,
        "active_model": active_model,
        "message": f"Local Ollama LLM ({active_model}) operational" if ollama_ready else "AI service operational using MoSPI domain knowledge base."
    }

@router.get("/health")
def get_ai_health():
    health = ollama_client.get_health()
    return health

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    payload: ChatRequest,
    db: Session = Depends(get_db)
):
    service = LearningAssistantService(db)
    try:
        response = service.chat(
            employee_id=payload.employee_id.upper(),
            message=payload.message,
            conversation_id=payload.conversation_id,
            document_id=payload.document_id,
            context_competency=payload.context_competency
        )
        return response
    except Exception as e:
        print(f"[API Chat Error] {e}")
        from datetime import datetime, timezone
        from app.ai.fallback_ai import fallback_ai
        fb = fallback_ai.get_assistant_response(
            user_message=payload.message,
            employee_name="Officer",
            job_role="Statistical Official"
        )
        return ChatResponse(
            conversation_id=payload.conversation_id or 1,
            message=fb["message"],
            role="assistant",
            sources=fb["sources"],
            model_used=fb["model_used"],
            created_at=datetime.now(timezone.utc)
        )

@router.get("/history/{employee_id}")
def get_chat_history(
    employee_id: str,
    db: Session = Depends(get_db)
):
    convs = db.query(AIConversation).filter(
        AIConversation.employee_id == employee_id.upper()
    ).order_by(AIConversation.updated_at.desc()).limit(10).all()

    results = []
    for c in convs:
        msgs = db.query(AIMessage).filter(
            AIMessage.conversation_id == c.id
        ).order_by(AIMessage.created_at.asc()).all()
        
        results.append({
            "conversation_id": c.id,
            "title": c.title,
            "updated_at": c.updated_at,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "sources": m.sources_json.get("sources", []) if m.sources_json else [],
                    "created_at": m.created_at
                } for m in msgs
            ]
        })
    return results
