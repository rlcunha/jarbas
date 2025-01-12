from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Avatar LLM API"
    DEBUG_MODE: bool = False
    API_V1_STR: str = "/api/v1"

    # Secrets
    OPENAI_API_KEY: str
    HUGGINGFACE_API_KEY: str

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Cache
    CACHE_EXPIRATION: int = 3600  # 1 hour
    VECTOR_CACHE_ENABLED: bool = True

    # LLM Config
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    LLM_MAX_CONTEXT_TOKENS: int = 4000

    # Avatar Config
    AVATAR_MODEL: str = "facebook/fastspeech2-en-ljspeech"
    AVATAR_TIMEOUT: float = 30.0
    AVATAR_MAX_RETRIES: int = 3

    # Azure Data Lake
    AZURE_STORAGE_ACCOUNT: str
    AZURE_STORAGE_KEY: str
    AZURE_CONTAINER_NAME: str = "data"

    # Azure Event Grid
    AZURE_EVENTGRID_ENDPOINT: Optional[str] = None
    AZURE_EVENTGRID_KEY: Optional[str] = None

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "jarbas-vectors"
    PINECONE_NAMESPACE: Optional[str] = None

    # Vector Search
    VECTOR_TOP_K: int = 5
    VECTOR_SIMILARITY_THRESHOLD: float = 0.7
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536

    # Prompt Templates
    DEFAULT_PROMPT_TEMPLATE: str = """
    Use o contexto abaixo para responder à pergunta. Se a resposta não puder ser encontrada no contexto, 
    responda que não tem informação suficiente para responder.

    Contexto:
    {context}

    Pergunta: {question}

    Resposta:"""

    class Config:
        env_file = "c:/Projetos/jarbas/backend/.env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()