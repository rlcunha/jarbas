import pytest
from app.services.data_lake_service import DataLakeService, DataLakeConfig
from app.services.vector_db_service import VectorDBService, VectorDBConfig
from app.services.vector_llm_service import VectorLLMService, VectorLLMConfig
from app.services.cache_service import CacheService
from app.utils.config import settings

"""
Plano de Teste de Integração da Stack

Este arquivo contém testes que validam a integração completa da stack,
seguindo o fluxo de dados desde a ingestão até a resposta ao usuário.

Fluxo de Teste:
1. Ingestão de Documento
   - Upload para Data Lake
   - Trigger de evento
   - Processamento e geração de embeddings
   - Armazenamento no banco vetorial

2. Consulta e Resposta
   - Busca vetorial
   - Recuperação de contexto
   - Geração de resposta
   - Cache

3. Validação de Performance
   - Tempo de resposta
   - Cache hit/miss
   - Qualidade das respostas
"""

@pytest.fixture
def services():
    """Inicializa todos os serviços necessários para os testes"""
    data_lake_config = DataLakeConfig(
        account_name=settings.AZURE_STORAGE_ACCOUNT,
        account_key=settings.AZURE_STORAGE_KEY,
        container_name=settings.AZURE_CONTAINER_NAME,
        event_grid_endpoint=settings.AZURE_EVENTGRID_ENDPOINT,
        event_grid_key=settings.AZURE_EVENTGRID_KEY
    )
    
    vector_db_config = VectorDBConfig(
        api_key=settings.PINECONE_API_KEY,
        environment=settings.PINECONE_ENVIRONMENT,
        index_name=settings.PINECONE_INDEX_NAME,
        embedding_dim=settings.EMBEDDING_DIMENSION
    )
    
    vector_llm_config = VectorLLMConfig(
        vector_db_config=vector_db_config.dict(),
        llm_config={
            "model": settings.LLM_MODEL,
            "temperature": settings.LLM_TEMPERATURE
        },
        max_context_tokens=settings.LLM_MAX_CONTEXT_TOKENS,
        use_cache=settings.VECTOR_CACHE_ENABLED
    )
    
    return {
        'data_lake': DataLakeService(data_lake_config),
        'vector_db': VectorDBService(vector_db_config),
        'vector_llm': VectorLLMService(vector_llm_config),
        'cache': CacheService()
    }

@pytest.mark.integration
class TestStackIntegration:
    """Testes de integração da stack completa"""
    
    @pytest.mark.asyncio
    async def test_document_ingestion_flow(self, services):
        """Testa o fluxo completo de ingestão de documentos"""
        # 1. Upload do documento
        test_content = "Este é um documento de teste sobre inteligência artificial."
        test_file = "test_doc.txt"
        
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # 2. Upload para o Data Lake
        upload_result = await services['data_lake'].upload_file(
            test_file,
            f"docs/{test_file}",
            {"type": "test", "subject": "AI"}
        )
        assert upload_result == True
        
        # 3. Lê o conteúdo do arquivo
        content = await services['data_lake'].read_file(f"docs/{test_file}")
        assert content.decode("utf-8") == test_content
        
        # 4. Gera embedding e armazena no banco vetorial
        embedding = await services['vector_db'].get_embedding(test_content)
        upsert_result = await services['vector_db'].upsert_vectors(
            vectors=[embedding],
            metadata=[{
                "content": test_content,
                "source": f"docs/{test_file}",
                "type": "test"
            }]
        )
        assert upsert_result == True

    @pytest.mark.asyncio
    async def test_query_response_flow(self, services):
        """Testa o fluxo completo de consulta e resposta"""
        # 1. Primeira consulta (cache miss)
        query = "O que é inteligência artificial?"
        response1 = await services['vector_llm'].get_response(query, "test_user")
        
        assert response1.cached == False
        assert len(response1.response) > 0
        assert len(response1.context) > 0
        
        # 2. Segunda consulta (cache hit)
        response2 = await services['vector_llm'].get_response(query, "test_user")
        assert response2.cached == True
        assert response2.response == response1.response

    @pytest.mark.asyncio
    async def test_performance_metrics(self, services):
        """Testa métricas de performance da stack"""
        import time
        
        # 1. Tempo de resposta sem cache
        query = "Qual a diferença entre IA e machine learning?"
        
        start_time = time.time()
        response = await services['vector_llm'].get_response(query, "test_user")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0  # Resposta deve ser menor que 5 segundos
        
        # 2. Tempo de resposta com cache
        start_time = time.time()
        cached_response = await services['vector_llm'].get_response(query, "test_user")
        end_time = time.time()
        
        cached_response_time = end_time - start_time
        assert cached_response_time < response_time
        assert cached_response_time < 1.0  # Cache deve responder em menos de 1 segundo

    @pytest.mark.asyncio
    async def test_error_recovery(self, services):
        """Testa recuperação de erros e fallbacks"""
        # 1. Teste com documento inexistente
        content = await services['data_lake'].read_file("inexistente.txt")
        assert content == b""
        
        # 2. Teste com query malformada
        response = await services['vector_llm'].get_response("", "test_user")
        assert "Desculpe" in response.response
        assert len(response.context) == 0

    def test_cleanup(self, services):
        """Limpa recursos utilizados nos testes"""
        import os
        
        # Remove arquivo de teste
        if os.path.exists("test_doc.txt"):
            os.remove("test_doc.txt")

"""
Instruções para Execução dos Testes de Integração:

1. Configure as variáveis de ambiente:
   - Copie .env.example para .env
   - Preencha todas as credenciais necessárias

2. Execute os testes:
   pytest -v tests/test_integration/test_stack_integration.py -m integration

3. Analise os resultados:
   - Verifique se todos os fluxos foram testados
   - Confirme os tempos de resposta
   - Valide a qualidade das respostas

4. Monitoramento:
   - Verifique logs do Azure
   - Monitore uso do Pinecone
   - Acompanhe métricas do Redis
"""