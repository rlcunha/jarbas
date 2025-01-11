import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.avatar_service import avatar_service
from app.models.schemas import AvatarResponse

async def test_avatar_service():
    try:
        text = "Olá, como posso ajudar?"
        response = await avatar_service.generate_avatar(text)
        print("\n=== Resultado do Teste ===")
        print(f"Avatar URL: {response.avatar_url}")
        print(f"Animation Data: {response.animation_data}")
        print("=========================\n")
    except Exception as e:
        print(f"\n=== Erro ===\n{str(e)}\n============\n")

if __name__ == "__main__":
    import asyncio
    import time
    
    asyncio.run(test_avatar_service())
    time.sleep(5)  # Manter a janela aberta por 5 segundos