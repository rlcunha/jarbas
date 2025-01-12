from typing import List, Optional
from pydantic import BaseModel
import numpy as np
import pinecone
from langchain.embeddings import OpenAIEmbeddings

class VectorDBConfig(BaseModel):
    api_key: str
    environment: str
    index_name: str
    embedding_dim: int = 1536  # Dimensão padrão do OpenAI embeddings
    namespace: Optional[str] = None

class VectorSearchResult(BaseModel):
    id: str
    content: str
    metadata: dict
    similarity: float

class VectorDBService:
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self.client = self._initialize_client()
        self.embeddings = OpenAIEmbeddings()
        
    def _initialize_client(self):
        """Inicializa o cliente Pinecone"""
        pinecone.init(
            api_key=self.config.api_key,
            environment=self.config.environment
        )
        
        # Verifica se o índice existe, se não, cria
        if self.config.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.config.index_name,
                dimension=self.config.embedding_dim,
                metric="cosine"
            )
            
        return pinecone.Index(self.config.index_name)

    async def upsert_vectors(self, 
                           vectors: List[np.ndarray], 
                           metadata: List[dict], 
                           ids: Optional[List[str]] = None) -> bool:
        """Insere ou atualiza vetores no Pinecone"""
        try:
            # Gera IDs se não fornecidos
            if ids is None:
                ids = [str(i) for i in range(len(vectors))]
                
            # Converte vetores numpy para listas
            vectors_list = [v.tolist() for v in vectors]
            
            # Prepara os dados no formato do Pinecone
            upsert_data = list(zip(ids, vectors_list, metadata))
            
            # Realiza upsert em batches de 100
            batch_size = 100
            for i in range(0, len(upsert_data), batch_size):
                batch = upsert_data[i:i + batch_size]
                self.client.upsert(
                    vectors=batch,
                    namespace=self.config.namespace
                )
                
            return True
        except Exception as e:
            print(f"Erro ao fazer upsert de vetores: {str(e)}")
            return False

    async def search_similar(self, 
                           query_vector: np.ndarray, 
                           top_k: int = 5) -> List[VectorSearchResult]:
        """Busca vetores similares no Pinecone"""
        try:
            # Converte vetor numpy para lista
            vector = query_vector.tolist()
            
            # Realiza a busca
            results = self.client.query(
                vector=vector,
                top_k=top_k,
                namespace=self.config.namespace,
                include_metadata=True
            )
            
            # Converte resultados para o formato VectorSearchResult
            search_results = []
            for match in results.matches:
                result = VectorSearchResult(
                    id=match.id,
                    content=match.metadata.get('content', ''),
                    metadata=match.metadata,
                    similarity=float(match.score)
                )
                search_results.append(result)
                
            return search_results
        except Exception as e:
            print(f"Erro ao buscar vetores similares: {str(e)}")
            return []

    async def delete_vectors(self, ids: List[str]) -> bool:
        """Remove vetores do Pinecone"""
        try:
            self.client.delete(
                ids=ids,
                namespace=self.config.namespace
            )
            return True
        except Exception as e:
            print(f"Erro ao deletar vetores: {str(e)}")
            return False

    async def get_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para um texto usando OpenAI"""
        try:
            embedding = await self.embeddings.aembed_query(text)
            return np.array(embedding)
        except Exception as e:
            print(f"Erro ao gerar embedding: {str(e)}")
            return np.zeros(self.config.embedding_dim)