from pydantic_settings import BaseSettings
from functools import lru_cache

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

    # LLM Config
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000

    # Avatar Config
    AVATAR_MODEL: str = "facebook/fastspeech2-en-ljspeech"
    AVATAR_TIMEOUT: float = 30.0
    AVATAR_MAX_RETRIES: int = 3

    class Config:
        env_file = "c:/Projetos/jarbas/backend/.env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()