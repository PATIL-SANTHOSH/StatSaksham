from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    sources: Optional[List[str]] = None
    created_at: Optional[datetime] = None

class ChatRequest(BaseModel):
    employee_id: str
    message: str
    conversation_id: Optional[int] = None
    document_id: Optional[int] = None
    context_competency: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    role: str = "assistant"
    sources: List[str] = []
    model_used: str
    created_at: datetime
