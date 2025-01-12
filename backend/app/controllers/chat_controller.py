from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import QuestionRequest, ChatResponse, VectorChatResponse
from app.services.llm_service import llm_service
from app.services.avatar_service import avatar_service
from app.services.cache_service import cache_service
from app.services.vector_llm_service import VectorLLMService, VectorLLMConfig
from app.utils.config import settings
import asyncio

router = APIRouter()

# Inicializa VectorLLMService
vector_llm_service = VectorLLMService(
    VectorLLMConfig(
        vector_db_config={
            "api_key": settings.PINECONE_API_KEY,
            "environment": settings.PINECONE_ENVIRONMENT,
            "index_name": settings.PINECONE_INDEX_NAME,
            "embedding_dim": settings.EMBEDDING_DIMENSION
        },
        llm_config={
            "model": settings.LLM_MODEL,
            "temperature": settings.LLM_TEMPERATURE
        },
        max_context_tokens=settings.LLM_MAX_CONTEXT_TOKENS,
        use_cache=settings.VECTOR_CACHE_ENABLED
    )
)

@router.post("/chat",
    response_model=ChatResponse,
    summary="Processar chat com avatar",
    description="Processa uma pergunta e retorna resposta com avatar animado",
    response_description="Resposta completa com texto e avatar",
    responses={
        200: {
            "description": "Resposta processada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "question": "Qual é a capital da França?",
                        "text_response": {
                            "text": "A capital da França é Paris.",
                            "confidence": 0.95
                        },
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
            }
        },
        500: {
            "description": "Erro ao processar a requisição"
        }
    }
)
async def process_chat(request: QuestionRequest):
    try:
        # Verificar cache
        cache_key = cache_service.generate_cache_key(
            request.question,
            request.user_id
        )

        cached_response = await cache_service.get_cached_response(cache_key)
        if cached_response:
            cached_response.cache_hit = True
            return cached_response

        # Processar pergunta com LLM e gerar avatar em paralelo
        llm_task = asyncio.create_task(
            llm_service.get_response(request.question)
        )

        llm_response = await llm_task

        # Gerar avatar com base na resposta do LLM
        avatar_response = await avatar_service.generate_avatar(
            llm_response.text
        )

        # Criar resposta completa
        response = ChatResponse(
            question=request.question,
            text_response=llm_response,
            avatar_response=avatar_response,
            cache_hit=False
        )

        # Salvar no cache
        await cache_service.set_cached_response(cache_key, response)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar chat: {str(e)}"
        )

@router.post("/ask",
    response_model=ChatResponse,
    summary="Processar pergunta simples",
    description="Processa uma pergunta e retorna resposta com avatar",
    response_description="Resposta textual com avatar",
    responses={
        200: {
            "description": "Resposta processada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "question": "Qual é a capital da França?",
                        "text_response": {
                            "text": "A capital da França é Paris.",
                            "confidence": 0.95
                        },
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
            }
        },
        500: {
            "description": "Erro ao processar a requisição"
        }
    }
)
async def ask_question(query: QuestionRequest):
    try:
        # Verificar cache
        cache_key = cache_service.generate_cache_key(
            query.question,
            query.user_id
        )

        cached_response = await cache_service.get_cached_response(cache_key)
        if cached_response:
            cached_response.cache_hit = True
            return cached_response

        # Processar pergunta com LLM
        llm_response = await llm_service.get_response(query.question)

        # Gerar avatar com base na resposta do LLM
        avatar_response = await avatar_service.generate_avatar(
            llm_response.text
        )

        # Criar resposta com avatar
        response = ChatResponse(
            question=query.question,
            text_response=llm_response,
            avatar_response=avatar_response,
            cache_hit=False
        )

        # Salvar no cache
        await cache_service.set_cached_response(cache_key, response)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )

@router.post("/vector-ask",
    response_model=VectorChatResponse,
    summary="Consultar banco vetorial com LLM",
    description="Processa uma pergunta usando o banco vetorial para contexto",
    response_description="Resposta com contexto e fontes",
    responses={
        200: {
            "description": "Resposta processada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "question": "O que é machine learning?",
                        "text_response": {
                            "text": "Machine Learning é um ramo da IA...",
                            "confidence": 0.95
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
            }
        },
        500: {
            "description": "Erro ao processar a requisição"
        }
    }
)
async def vector_ask_question(query: QuestionRequest):
    try:
        # Obter resposta do VectorLLM
        vector_response = await vector_llm_service.get_response(
            query.question,
            query.user_id
        )

        # Gerar avatar com base na resposta
        avatar_response = await avatar_service.generate_avatar(
            vector_response.response
        )

        # Criar resposta completa
        response = VectorChatResponse(
            question=query.question,
            text_response=LLMResponse(
                text=vector_response.response,
                confidence=0.95,
                metadata={"sources": vector_response.sources}
            ),
            context=vector_response.context,
            sources=vector_response.sources,
            avatar_response=avatar_response,
            cache_hit=vector_response.cached
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar pergunta vetorial: {str(e)}"
        )