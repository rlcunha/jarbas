from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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

class VectorChatResponse(ChatResponse):
    """Estende ChatResponse para incluir contexto e fontes do banco vetorial"""
    context: List[str] = Field(
        default_factory=list,
        description="Lista de trechos de texto usados como contexto para a resposta"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="Lista de fontes dos documentos usados como contexto"
    )

    class Config:
        schema_extra = {
            "example": {
                "question": "O que é machine learning?",
                "text_response": {
                    "text": "Machine Learning é um ramo da Inteligência Artificial...",
                    "confidence": 0.95,
                    "metadata": {
                        "sources": ["docs/ml_intro.pdf", "docs/ai_examples.txt"]
                    }
                },
                "context": [
                    "Machine Learning é uma tecnologia que permite...",
                    "Exemplos de aplicações incluem..."
                ],
                "sources": [
                    "docs/ml_intro.pdf",
                    "docs/ai_examples.txt"
                ],
                "avatar_response": {
                    "avatar_url": "http://localhost:8000/audio/temp_audio.wav",
                    "animation_data": {
                        "duration": 5.2
                    }
                },
                "timestamp": "2025-01-10T23:11:04.156558",
                "cache_hit": False
            }
        }