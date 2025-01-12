import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.services.vector_db_service import VectorDBService, VectorDBConfig, VectorSearchResult

@pytest.fixture
def mock_pinecone():
    with patch('pinecone.init') as mock_init, \
         patch('pinecone.Index') as mock_index:
        yield {
            'init': mock_init,
            'index': mock_index
        }

@pytest.fixture
def vector_db_config():
    return VectorDBConfig(
        api_key="test-key",
        environment="test-env",
        index_name="test-index",
        embedding_dim=1536
    )

@pytest.fixture
def vector_db_service(mock_pinecone, vector_db_config):
    return VectorDBService(vector_db_config)

def test_initialize_client(mock_pinecone, vector_db_config):
    service = VectorDBService(vector_db_config)
    
    mock_pinecone['init'].assert_called_once_with(
        api_key=vector_db_config.api_key,
        environment=vector_db_config.environment
    )
    mock_pinecone['index'].assert_called_once_with(vector_db_config.index_name)

@pytest.mark.asyncio
async def test_upsert_vectors_success(vector_db_service):
    vectors = [np.array([0.1, 0.2]), np.array([0.3, 0.4])]
    metadata = [{"source": "doc1"}, {"source": "doc2"}]
    ids = ["1", "2"]
    
    vector_db_service.client.upsert = Mock(return_value=None)
    
    result = await vector_db_service.upsert_vectors(vectors, metadata, ids)
    
    assert result == True
    vector_db_service.client.upsert.assert_called_once()
    call_args = vector_db_service.client.upsert.call_args[1]
    assert len(call_args['vectors']) == 2

@pytest.mark.asyncio
async def test_search_similar_success(vector_db_service):
    mock_matches = [
        Mock(
            id="1",
            metadata={"content": "test content", "source": "doc1"},
            score=0.9
        )
    ]
    vector_db_service.client.query = Mock(
        return_value=Mock(matches=mock_matches)
    )
    
    query_vector = np.array([0.1, 0.2])
    results = await vector_db_service.search_similar(query_vector, top_k=1)
    
    assert len(results) == 1
    assert isinstance(results[0], VectorSearchResult)
    assert results[0].id == "1"
    assert results[0].content == "test content"
    assert results[0].similarity == 0.9

@pytest.mark.asyncio
async def test_delete_vectors_success(vector_db_service):
    vector_db_service.client.delete = Mock(return_value=None)
    
    result = await vector_db_service.delete_vectors(["1", "2"])
    
    assert result == True
    vector_db_service.client.delete.assert_called_once_with(
        ids=["1", "2"],
        namespace=None
    )

@pytest.mark.asyncio
async def test_get_embedding_success(vector_db_service):
    test_embedding = [0.1] * 1536
    vector_db_service.embeddings.aembed_query = Mock(
        return_value=test_embedding
    )
    
    result = await vector_db_service.get_embedding("test text")
    
    assert isinstance(result, np.ndarray)
    assert result.shape == (1536,)
    vector_db_service.embeddings.aembed_query.assert_called_once_with("test text")

@pytest.mark.asyncio
async def test_error_handling(vector_db_service):
    # Teste de erro no upsert
    vector_db_service.client.upsert = Mock(side_effect=Exception("Erro teste"))
    result = await vector_db_service.upsert_vectors(
        [np.array([0.1, 0.2])],
        [{"source": "doc1"}],
        ["1"]
    )
    assert result == False
    
    # Teste de erro na busca
    vector_db_service.client.query = Mock(side_effect=Exception("Erro teste"))
    results = await vector_db_service.search_similar(np.array([0.1, 0.2]))
    assert results == []
    
    # Teste de erro na deleção
    vector_db_service.client.delete = Mock(side_effect=Exception("Erro teste"))
    result = await vector_db_service.delete_vectors(["1"])
    assert result == False