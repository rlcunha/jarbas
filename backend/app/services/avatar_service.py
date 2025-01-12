import httpx
from app.utils.config import settings
from app.models.schemas import AvatarResponse
from typing import Dict, Any

class AvatarService:
    def __init__(self):
        self.model = settings.AVATAR_MODEL if hasattr(settings, 'AVATAR_MODEL') else "facebook/fastspeech2-en-ljspeech"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
        }
        self.timeout = settings.AVATAR_TIMEOUT if hasattr(settings, 'AVATAR_TIMEOUT') else 30.0
        self.max_retries = settings.AVATAR_MAX_RETRIES if hasattr(settings, 'AVATAR_MAX_RETRIES') else 3

    async def generate_avatar(self, text: str) -> AvatarResponse:
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "inputs": text,
                    "options": {
                        "use_cache": True,
                        "wait_for_model": True
                    }
                }

                # Tentar até 3 vezes com espera entre as tentativas
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.post(
                            self.api_url,
                            headers=self.headers,
                            json=payload,
                            timeout=30.0
                        )
                        response.raise_for_status()
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 503 and attempt < max_retries - 1:
                            await asyncio.sleep(5)  # Esperar 5 segundos antes de tentar novamente
                            continue
                        raise

                response.raise_for_status()
                
                # Salvar o arquivo de áudio temporariamente
                import uuid
                import os
                
                audio_file = f"temp_{uuid.uuid4().hex}.wav"
                with open(audio_file, "wb") as f:
                    f.write(response.content)
                
                # Criar uma função de limpeza para remover o arquivo temporário
                import atexit
                import os
                
                def cleanup(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                
                atexit.register(cleanup, audio_file)
                
                return AvatarResponse(
                    avatar_url=audio_file,
                    animation_data={"audio_file": audio_file}
                )
        except Exception as e:
            raise Exception(f"Erro ao gerar avatar: {str(e)}")

avatar_service = AvatarService()