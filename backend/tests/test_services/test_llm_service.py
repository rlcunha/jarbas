import pytest
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.llm_service import llm_service
from app.models.schemas import LLMResponse

async def test_llm_service():
    try:
        question = "Qual é a capital da França?"
        response = await llm_service.get_response(question)
        print("\n=== Resultado do Teste ===")
        print(f"Resposta: {response.text}")
        print(f"Confiança: {response.confidence}")
        print(f"Metadados: {response.metadata}")
        print("=========================\n")
    except Exception as e:
        print(f"\n=== Erro ===\n{str(e)}\n============\n")

if __name__ == "__main__":
    import asyncio
    import time
    
    asyncio.run(test_llm_service())
    time.sleep(5)  # Manter a janela aberta por 5 segundos