from typing import List, Optional
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import EventGridEvent
from azure.core.credentials import AzureKeyCredential
from pydantic import BaseModel
import json

class DataLakeConfig(BaseModel):
    account_name: str
    account_key: str
    container_name: str
    event_grid_endpoint: Optional[str] = None
    event_grid_key: Optional[str] = None

class DataLakeFile(BaseModel):
    name: str
    size: int
    last_modified: str
    content_type: Optional[str] = None
    metadata: Optional[dict] = None

class DataLakeService:
    def __init__(self, config: DataLakeConfig):
        self.config = config
        self.client = self._initialize_client()
        self.event_grid_client = self._initialize_event_grid() if config.event_grid_endpoint else None
        self.file_system_client = self.client.get_file_system_client(self.config.container_name)

    def _initialize_client(self) -> DataLakeServiceClient:
        """Inicializa o cliente do Azure Data Lake"""
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.config.account_name};"
            f"AccountKey={self.config.account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        return DataLakeServiceClient.from_connection_string(connection_string)

    def _initialize_event_grid(self) -> EventGridClient:
        """Inicializa o cliente do Azure Event Grid"""
        if not self.config.event_grid_key:
            return None
        
        credential = AzureKeyCredential(self.config.event_grid_key)
        return EventGridClient(credential)

    async def list_files(self, directory: str) -> List[DataLakeFile]:
        """Lista arquivos em um diretório do Data Lake"""
        try:
            directory_client = self.file_system_client.get_directory_client(directory)
            paths = directory_client.get_paths(recursive=True)
            
            files = []
            for path in paths:
                if not path.is_directory:
                    file_client = self.file_system_client.get_file_client(path.name)
                    properties = file_client.get_file_properties()
                    
                    file = DataLakeFile(
                        name=path.name,
                        size=properties.size,
                        last_modified=properties.last_modified.isoformat(),
                        content_type=properties.content_settings.content_type,
                        metadata=properties.metadata
                    )
                    files.append(file)
                    
            return files
        except Exception as e:
            print(f"Erro ao listar arquivos: {str(e)}")
            return []

    async def read_file(self, file_path: str) -> bytes:
        """Lê o conteúdo de um arquivo do Data Lake"""
        try:
            file_client = self.file_system_client.get_file_client(file_path)
            download = file_client.download_file()
            return download.readall()
        except Exception as e:
            print(f"Erro ao ler arquivo: {str(e)}")
            return b""

    async def upload_file(self, local_path: str, remote_path: str, metadata: Optional[dict] = None) -> bool:
        """Faz upload de um arquivo para o Data Lake e dispara evento"""
        try:
            # Cria o cliente do arquivo
            file_client = self.file_system_client.get_file_client(remote_path)
            
            # Lê o arquivo local
            with open(local_path, "rb") as data:
                file_client.upload_data(data, overwrite=True)
            
            # Adiciona metadata se fornecido
            if metadata:
                file_client.set_metadata(metadata)
            
            # Dispara evento de upload
            await self._publish_file_event("FileCreated", remote_path, metadata)
            
            return True
        except Exception as e:
            print(f"Erro ao fazer upload: {str(e)}")
            return False

    async def delete_file(self, file_path: str) -> bool:
        """Remove um arquivo do Data Lake e dispara evento"""
        try:
            file_client = self.file_system_client.get_file_client(file_path)
            file_client.delete_file()
            
            # Dispara evento de deleção
            await self._publish_file_event("FileDeleted", file_path)
            
            return True
        except Exception as e:
            print(f"Erro ao deletar arquivo: {str(e)}")
            return False

    async def _publish_file_event(self, event_type: str, file_path: str, metadata: Optional[dict] = None) -> None:
        """Publica evento no Event Grid"""
        if not self.event_grid_client or not self.config.event_grid_endpoint:
            return
        
        try:
            event = EventGridEvent(
                id=str(datetime.utcnow().timestamp()),
                subject=f"/datalake/{self.config.container_name}/{file_path}",
                data={
                    "api": "DataLake",
                    "path": file_path,
                    "metadata": metadata or {}
                },
                event_type=f"DataLake.{event_type}",
                event_time=datetime.utcnow(),
                data_version="1.0"
            )
            
            self.event_grid_client.publish_events(
                self.config.event_grid_endpoint,
                [event]
            )
        except Exception as e:
            print(f"Erro ao publicar evento: {str(e)}")

    async def get_file_metadata(self, file_path: str) -> Optional[dict]:
        """Obtém metadados de um arquivo"""
        try:
            file_client = self.file_system_client.get_file_client(file_path)
            properties = file_client.get_file_properties()
            return properties.metadata
        except Exception as e:
            print(f"Erro ao obter metadados: {str(e)}")
            return None