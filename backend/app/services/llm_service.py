from app.utils.config import settings
from app.models.schemas import LLMResponse
from openai import OpenAI
import asyncio

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0
        )
        self.model = settings.LLM_MODEL if hasattr(settings, 'LLM_MODEL') else "gpt-3.5-turbo"
        self.temperature = settings.LLM_TEMPERATURE if hasattr(settings, 'LLM_TEMPERATURE') else 0.7
        self.max_tokens = settings.LLM_MAX_TOKENS if hasattr(settings, 'LLM_MAX_TOKENS') else 1000

    async def get_response(self, question: str) -> LLMResponse:
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente útil."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7
            )

            return LLMResponse(
                text=response.choices[0].message.content,
                confidence=0.95,
                metadata={
                    "model": self.model,
                    "usage": response.usage
                }
            )
        except Exception as e:
            raise Exception(f"Erro ao processar LLM: {str(e)}")

llm_service = LLMService()