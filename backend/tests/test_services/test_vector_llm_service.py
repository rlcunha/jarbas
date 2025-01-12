import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from app.services.vector_llm_service import (
    VectorLLMService,
    VectorLLMConfig,
    VectorLLMResponse
)
from app.models.schemas import ChatResponse, LLMResponse

@pytest.fixture
def vector_llm_config():
    return VectorLLMConfig(
        vector_db_config={
            "api_key": "test-key",
            "environment": "test-env",
            "index_name": "test-index"
        },
        llm_config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        },
        max_context_tokens=4000,
        use_cache=True
    )

@pytest.fixture
def mock_services():
    with patch('app.services.vector_llm_service.VectorDBService') as mock_vector_db, \
         patch('app.services.vector_llm_service.LLMService') as mock_llm, \
         patch('app.services.vector_llm_service.cache_service') as mock_cache, \
         patch('app.services.vector_llm_service.ChatOpenAI') as mock_chat_openai, \
         patch('app.services.vector_llm_service.LLMChain') as mock_llm_chain:
        
        yield {
            'vector_db': mock_vector_db,
            'llm': mock_llm,
            'cache': mock_cache,
            'chat_openai': mock_chat_openai,
            'llm_chain': mock_llm_chain
        }

@pytest.fixture
def vector_llm_service(mock_services, vector_llm_config):
    service = VectorLLMService(vector_llm_config)
    # Configura mocks para os atributos do serviço
    service.chain = MagicMock()
    return service

@pytest.mark.asyncio
async def test_get_response_with_cache_hit(vector_llm_service, mock_services):
    # Configura mock do cache para simular hit
    cached_response = ChatResponse(
        text="cached response",
        context=["context1"],
        sources=["source1"]
    )
    mock_services['cache'].get_cached_response.return_value = cached_response
    
    response = await vector_llm_service.get_response("test query", "user1")
    
    assert isinstance(response, VectorLLMResponse)
    assert response.response == "cached response"
    assert response.cached == True
    mock_services['cache'].get_cached_response.assert_called_once()

@pytest.mark.asyncio
async def test_get_response_with_cache_miss(vector_llm_service, mock_services):
    # Configura mock do cache para simular miss
    mock_services['cache'].get_cached_response.return_value = None
    
    # Configura mocks para o fluxo completo
    mock_embedding = np.array([0.1] * 1536)
    vector_llm_service._embed_query = Mock(return_value=mock_embedding)
    
    mock_context = [
        Mock(
            content="test context",
            metadata={"source": "test source"},
            similarity=0.9
        )
    ]
    vector_llm_service._get_relevant_context = Mock(return_value=mock_context)
    
    vector_llm_service.chain.arun = Mock(return_value="test response")
    
    response = await vector_llm_service.get_response("test query", "user1")
    
    assert isinstance(response, VectorLLMResponse)
    assert response.response == "test response"
    assert response.cached == False
    assert "test context" in response.context
    assert "test source" in response.sources

@pytest.mark.asyncio
async def test_embed_query(vector_llm_service):
    mock_embedding = [0.1] * 1536
    vector_llm_service.embeddings.aembed_query = Mock(return_value=mock_embedding)
    
    result = await vector_llm_service._embed_query("test query")
    
    assert isinstance(result, np.ndarray)
    assert result.shape == (1536,)
    vector_llm_service.embeddings.aembed_query.assert_called_once_with("test query")

@pytest.mark.asyncio
async def test_get_relevant_context(vector_llm_service):
    mock_results = [
        Mock(
            content="test context",
            metadata={"source": "test source"},
            similarity=0.9
        )
    ]
    vector_llm_service.vector_db.search_similar = Mock(return_value=mock_results)
    
    query_vector = np.array([0.1] * 1536)
    results = await vector_llm_service._get_relevant_context(query_vector)
    
    assert len(results) == 1
    assert results[0].content == "test context"
    vector_llm_service.vector_db.search_similar.assert_called_once()

def test_format_context(vector_llm_service):
    mock_results = [
        Mock(
            content="test context 1",
            metadata={"source": "source1"},
            similarity=0.9
        ),
        Mock(
            content="test context 2",
            metadata={"source": "source2"},
            similarity=0.8
        )
    ]
    
    formatted = vector_llm_service._format_context(mock_results)
    
    assert isinstance(formatted, str)
    assert "test context 1" in formatted
    assert "source1" in formatted
    assert "test context 2" in formatted
    assert "source2" in formatted

@pytest.mark.asyncio
async def test_error_handling(vector_llm_service, mock_services):
    # Simula erro no embedding
    vector_llm_service._embed_query = Mock(side_effect=Exception("Erro teste"))
    
    response = await vector_llm_service.get_response("test query")
    
    assert "Desculpe, ocorreu um erro" in response.response
    assert response.context == []
    assert response.sources == []

@pytest.mark.asyncio
async def test_integration_flow(vector_llm_service, mock_services):
    # Configura mocks para testar o fluxo completo
    mock_services['cache'].get_cached_response.return_value = None
    
    mock_embedding = np.array([0.1] * 1536)
    vector_llm_service._embed_query = Mock(return_value=mock_embedding)
    
    mock_context = [
        Mock(
            content="test context",
            metadata={"source": "test source"},
            similarity=0.9
        )
    ]
    vector_llm_service._get_relevant_context = Mock(return_value=mock_context)
    
    vector_llm_service.chain.arun = Mock(return_value="test response")
    
    # Executa o fluxo completo
    response = await vector_llm_service.get_response("test query", "user1")
    
    # Verifica se cada etapa foi chamada na ordem correta
    mock_services['cache'].get_cached_response.assert_called_once()
    vector_llm_service._embed_query.assert_called_once()
    vector_llm_service._get_relevant_context.assert_called_once()
    vector_llm_service.chain.arun.assert_called_once()
    mock_services['cache'].set_cached_response.assert_called_once()