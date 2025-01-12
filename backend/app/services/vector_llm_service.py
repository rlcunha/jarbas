from typing import List, Optional
from pydantic import BaseModel
import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from .vector_db_service import VectorDBService, VectorSearchResult
from .llm_service import LLMService
from .cache_service import cache_service
from app.models.schemas import ChatResponse

DEFAULT_PROMPT_TEMPLATE = """
Use o contexto abaixo para responder à pergunta. Se a resposta não puder ser encontrada no contexto, 
responda que não tem informação suficiente para responder.

Contexto:
{context}

Pergunta: {question}

Resposta:"""

class VectorLLMConfig(BaseModel):
    vector_db_config: dict
    llm_config: dict
    max_context_tokens: int = 4000
    prompt_template: Optional[str] = DEFAULT_PROMPT_TEMPLATE
    use_cache: bool = True

class VectorLLMResponse(BaseModel):
    response: str
    context: List[str]
    sources: List[str]
    cached: bool = False

class VectorLLMService:
    def __init__(self, config: VectorLLMConfig):
        self.config = config
        self.vector_db = VectorDBService(config.vector_db_config)
        self.llm = LLMService()
        self.embeddings = OpenAIEmbeddings()
        self.prompt = PromptTemplate(
            template=config.prompt_template,
            input_variables=["context", "question"]
        )
        
        # Configura LangChain
        self.langchain_llm = ChatOpenAI(
            temperature=0.7,
            model_name=self.llm.model
        )
        self.chain = LLMChain(
            llm=self.langchain_llm,
            prompt=self.prompt
        )

    async def get_response(self, 
                          query: str, 
                          user_id: Optional[str] = None) -> VectorLLMResponse:
        """Obtém resposta do LLM com contexto do banco vetorial"""
        
        # Verifica cache se habilitado
        if self.config.use_cache:
            cache_key = cache_service.generate_cache_key(query, user_id)
            cached_response = await cache_service.get_cached_response(cache_key)
            if cached_response:
                return VectorLLMResponse(
                    response=cached_response.text,
                    context=cached_response.context or [],
                    sources=cached_response.sources or [],
                    cached=True
                )
        
        try:
            # 1. Converter query em vetor
            query_vector = await self._embed_query(query)
            
            # 2. Buscar contexto relevante
            context_results = await self._get_relevant_context(query_vector)
            
            # 3. Formatar contexto e prompt
            formatted_context = self._format_context(context_results)
            
            # 4. Obter resposta via LangChain
            chain_response = await self.chain.arun({
                "context": formatted_context,
                "question": query
            })
            
            response = VectorLLMResponse(
                response=chain_response,
                context=[c.content for c in context_results],
                sources=[c.metadata.get('source', '') for c in context_results]
            )
            
            # Salva no cache se habilitado
            if self.config.use_cache:
                await cache_service.set_cached_response(
                    cache_key,
                    ChatResponse(
                        text=response.response,
                        context=response.context,
                        sources=response.sources
                    )
                )
            
            return response
            
        except Exception as e:
            print(f"Erro ao processar resposta: {str(e)}")
            return VectorLLMResponse(
                response="Desculpe, ocorreu um erro ao processar sua pergunta.",
                context=[],
                sources=[]
            )

    async def _embed_query(self, text: str) -> np.ndarray:
        """Converte texto em vetor de embeddings usando LangChain"""
        try:
            embedding = await self.embeddings.aembed_query(text)
            return np.array(embedding)
        except Exception as e:
            print(f"Erro ao gerar embedding: {str(e)}")
            return np.zeros(1536)  # Dimensão padrão OpenAI

    async def _get_relevant_context(self, 
                                  query_vector: np.ndarray, 
                                  top_k: int = 5) -> List[VectorSearchResult]:
        """Obtém contexto relevante do banco vetorial"""
        return await self.vector_db.search_similar(query_vector, top_k)

    def _format_context(self, context_results: List[VectorSearchResult]) -> str:
        """Formata o contexto para inclusão no prompt"""
        formatted_contexts = []
        total_chars = 0
        char_limit = self.config.max_context_tokens * 4  # Estimativa aproximada
        
        for result in context_results:
            context_text = f"[Fonte: {result.metadata.get('source', 'Desconhecida')}]\n{result.content}"
            if total_chars + len(context_text) > char_limit:
                break
                
            formatted_contexts.append(context_text)
            total_chars += len(context_text)
            
        return "\n\n".join(formatted_contexts)