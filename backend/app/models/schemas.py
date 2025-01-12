from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class AvatarResponse(BaseModel):
    avatar_url: str
    animation_data: Dict[str, Any]

class LLMResponse(BaseModel):
    text: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    question: str
    text_response: LLMResponse
    avatar_response: Optional[AvatarResponse] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cache_hit: bool = False