import redis
import json
from app.utils.config import settings
from app.models.schemas import ChatResponse
from typing import Optional

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    async def get_cached_response(self, key: str) -> Optional[ChatResponse]:
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return ChatResponse.parse_raw(cached_data)
            return None
        except Exception as e:
            print(f"Erro ao recuperar cache: {str(e)}")
            return None

    async def set_cached_response(self, key: str, response: ChatResponse) -> bool:
        try:
            self.redis_client.setex(
                key,
                settings.CACHE_EXPIRATION,
                response.json()
            )
            return True
        except Exception as e:
            print(f"Erro ao definir cache: {str(e)}")
            return False

    def generate_cache_key(self, question: str, user_id: Optional[str] = None) -> str:
        base_key = question.lower().strip()
        if user_id:
            return f"chat:{user_id}:{base_key}"
        return f"chat:{base_key}"

cache_service = CacheService()