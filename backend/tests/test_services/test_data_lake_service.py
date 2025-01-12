import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.services.data_lake_service import DataLakeService, DataLakeConfig, DataLakeFile

@pytest.fixture
def data_lake_config():
    return DataLakeConfig(
        account_name="testaccount",
        account_key="testkey",
        container_name="testcontainer",
        event_grid_endpoint="https://test.eventgrid.azure.net",
        event_grid_key="eventgridkey"
    )

@pytest.fixture
def mock_data_lake():
    with patch('azure.storage.filedatalake.DataLakeServiceClient') as mock_client, \
         patch('azure.eventgrid.EventGridClient') as mock_eventgrid:
        mock_filesystem = MagicMock()
        mock_client.from_connection_string.return_value.get_file_system_client.return_value = mock_filesystem
        
        yield {
            'client': mock_client,
            'filesystem': mock_filesystem,
            'eventgrid': mock_eventgrid
        }

@pytest.fixture
def data_lake_service(mock_data_lake, data_lake_config):
    return DataLakeService(data_lake_config)

def test_initialize_client(mock_data_lake, data_lake_config):
    service = DataLakeService(data_lake_config)
    
    mock_data_lake['client'].from_connection_string.assert_called_once()
    connection_string = mock_data_lake['client'].from_connection_string.call_args[0][0]
    assert data_lake_config.account_name in connection_string
    assert data_lake_config.account_key in connection_string

@pytest.mark.asyncio
async def test_list_files_success(data_lake_service, mock_data_lake):
    # Configura mock para simular arquivos
    mock_path = MagicMock()
    mock_path.is_directory = False
    mock_path.name = "test.txt"
    
    mock_properties = MagicMock()
    mock_properties.size = 1024
    mock_properties.last_modified = datetime.now()
    mock_properties.content_settings.content_type = "text/plain"
    mock_properties.metadata = {"key": "value"}
    
    mock_file_client = MagicMock()
    mock_file_client.get_file_properties.return_value = mock_properties
    
    mock_data_lake['filesystem'].get_paths.return_value = [mock_path]
    mock_data_lake['filesystem'].get_file_client.return_value = mock_file_client
    
    files = await data_lake_service.list_files("test-dir")
    
    assert len(files) == 1
    assert isinstance(files[0], DataLakeFile)
    assert files[0].name == "test.txt"
    assert files[0].size == 1024

@pytest.mark.asyncio
async def test_read_file_success(data_lake_service, mock_data_lake):
    mock_download = MagicMock()
    mock_download.readall.return_value = b"test content"
    
    mock_file_client = MagicMock()
    mock_file_client.download_file.return_value = mock_download
    
    mock_data_lake['filesystem'].get_file_client.return_value = mock_file_client
    
    content = await data_lake_service.read_file("test.txt")
    
    assert content == b"test content"
    mock_file_client.download_file.assert_called_once()

@pytest.mark.asyncio
async def test_upload_file_success(data_lake_service, mock_data_lake):
    mock_file_client = MagicMock()
    mock_data_lake['filesystem'].get_file_client.return_value = mock_file_client
    
    # Mock open() usando context manager
    mock_file = MagicMock()
    with patch('builtins.open', return_value=mock_file):
        result = await data_lake_service.upload_file(
            "local/test.txt",
            "remote/test.txt",
            {"metadata": "value"}
        )
    
    assert result == True
    mock_file_client.upload_data.assert_called_once()
    mock_file_client.set_metadata.assert_called_once_with({"metadata": "value"})

@pytest.mark.asyncio
async def test_delete_file_success(data_lake_service, mock_data_lake):
    mock_file_client = MagicMock()
    mock_data_lake['filesystem'].get_file_client.return_value = mock_file_client
    
    result = await data_lake_service.delete_file("test.txt")
    
    assert result == True
    mock_file_client.delete_file.assert_called_once()

@pytest.mark.asyncio
async def test_event_grid_integration(data_lake_service, mock_data_lake):
    # Mock para o Event Grid
    mock_eventgrid_client = MagicMock()
    data_lake_service.event_grid_client = mock_eventgrid_client
    
    # Testa publicação de evento após upload
    mock_file_client = MagicMock()
    mock_data_lake['filesystem'].get_file_client.return_value = mock_file_client
    
    with patch('builtins.open', MagicMock()):
        await data_lake_service.upload_file(
            "local/test.txt",
            "remote/test.txt",
            {"metadata": "value"}
        )
    
    # Verifica se o evento foi publicado
    mock_eventgrid_client.publish_events.assert_called_once()
    event = mock_eventgrid_client.publish_events.call_args[0][1][0]
    assert event.event_type == "DataLake.FileCreated"
    assert "remote/test.txt" in event.subject

@pytest.mark.asyncio
async def test_error_handling(data_lake_service, mock_data_lake):
    # Teste de erro na listagem
    mock_data_lake['filesystem'].get_paths.side_effect = Exception("Erro teste")
    files = await data_lake_service.list_files("test-dir")
    assert files == []
    
    # Teste de erro na leitura
    mock_data_lake['filesystem'].get_file_client.return_value.download_file.side_effect = Exception("Erro teste")
    content = await data_lake_service.read_file("test.txt")
    assert content == b""
    
    # Teste de erro no upload
    mock_data_lake['filesystem'].get_file_client.return_value.upload_data.side_effect = Exception("Erro teste")
    with patch('builtins.open', MagicMock()):
        result = await data_lake_service.upload_file("local.txt", "remote.txt")
    assert result == False
    
    # Teste de erro na deleção
    mock_data_lake['filesystem'].get_file_client.return_value.delete_file.side_effect = Exception("Erro teste")
    result = await data_lake_service.delete_file("test.txt")
    assert result == False