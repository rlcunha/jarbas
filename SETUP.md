# Guia de Configuração da Stack

Este guia detalha o passo a passo para configurar cada componente da stack.

## 1. Azure Data Lake Storage

### 1.1 Criar Recursos no Azure
1. Acesse o [Portal Azure](https://portal.azure.com)
2. Crie um novo recurso "Storage Account":
   - Tipo: StorageV2 (general purpose v2)
   - Performance: Standard
   - Replication: LRS (Locally redundant storage)
   - Access tier: Hot

3. Após criar o Storage Account:
   - Vá em "Access keys"
   - Copie a "Connection string" ou "Account key"
   - Crie um container chamado "data"

### 1.2 Configurar Event Grid (Opcional)
1. No Portal Azure:
   - Vá para "Events" no seu Storage Account
   - Clique em "Event Subscription"
   - Selecione o tipo de evento "Blob Created"
   - Configure o endpoint (sua Azure Function)

### 1.3 Variáveis de Ambiente
```env
AZURE_STORAGE_ACCOUNT=nome-da-sua-conta
AZURE_STORAGE_KEY=sua-chave-de-acesso
AZURE_CONTAINER_NAME=data
AZURE_EVENTGRID_ENDPOINT=https://sua-function.azurewebsites.net/api/trigger
AZURE_EVENTGRID_KEY=sua-chave-event-grid
```

## 2. Pinecone (Banco Vetorial)

### 2.1 Criar Conta Pinecone
1. Acesse [Pinecone](https://www.pinecone.io/)
2. Crie uma conta gratuita
3. Crie um novo projeto
4. Crie um índice:
   - Dimensão: 1536 (padrão OpenAI embeddings)
   - Metric: cosine
   - Pod type: starter

### 2.2 Obter Credenciais
1. No dashboard do Pinecone:
   - Copie sua API key
   - Note seu environment
   - Copie o nome do índice criado

### 2.3 Variáveis de Ambiente
```env
PINECONE_API_KEY=sua-api-key
PINECONE_ENVIRONMENT=seu-environment
PINECONE_INDEX_NAME=seu-index-name
PINECONE_NAMESPACE=opcional
```

## 3. OpenAI

### 3.1 Criar Conta OpenAI
1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Crie uma conta
3. Vá para "API Keys"
4. Crie uma nova chave secreta

### 3.2 Variáveis de Ambiente
```env
OPENAI_API_KEY=sua-api-key
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_MAX_CONTEXT_TOKENS=4000
```

## 4. Redis (Cache)

### 4.1 Opção 1: Docker Local
```bash
# No arquivo docker-compose.yml
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

### 4.2 Opção 2: Redis Cloud
1. Acesse [Redis Cloud](https://redis.com/try-free/)
2. Crie uma conta gratuita
3. Crie um novo banco de dados
4. Obtenha as credenciais de conexão

### 4.3 Variáveis de Ambiente
```env
REDIS_HOST=localhost # ou seu host na nuvem
REDIS_PORT=6379
CACHE_EXPIRATION=3600
```

## 5. Configuração Completa

### 5.1 Arquivo .env
1. Copie o arquivo .env.example:
```bash
cp backend/.env.example backend/.env
```

2. Preencha com todas as credenciais obtidas:
```env
# App
DEBUG_MODE=false

# OpenAI
OPENAI_API_KEY=sua-openai-key
HUGGINGFACE_API_KEY=opcional

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_EXPIRATION=3600

# LLM
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
LLM_MAX_CONTEXT_TOKENS=4000

# Azure Data Lake
AZURE_STORAGE_ACCOUNT=sua-conta
AZURE_STORAGE_KEY=sua-chave
AZURE_CONTAINER_NAME=data

# Azure Event Grid (opcional)
AZURE_EVENTGRID_ENDPOINT=sua-function-url
AZURE_EVENTGRID_KEY=sua-chave

# Pinecone
PINECONE_API_KEY=sua-pinecone-key
PINECONE_ENVIRONMENT=seu-environment
PINECONE_INDEX_NAME=seu-index
PINECONE_NAMESPACE=opcional

# Vector Search
VECTOR_TOP_K=5
VECTOR_SIMILARITY_THRESHOLD=0.7
VECTOR_CACHE_ENABLED=true
EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_DIMENSION=1536
```

### 5.2 Instalação de Dependências
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 5.3 Inicialização dos Serviços
```bash
# Terminal 1 - Redis
docker-compose up redis

# Terminal 2 - Backend
cd backend
uvicorn main:app --reload

# Terminal 3 - Frontend
cd frontend
npm run dev
```

## 6. Validação da Configuração

### 6.1 Testar Conexões
```bash
# Execute os testes de integração
pytest backend/tests/test_integration/test_stack_integration.py -m integration
```

### 6.2 Testar API
```bash
# Teste do endpoint vector-ask
curl -X POST http://localhost:8000/api/v1/vector-ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é machine learning?", "user_id": "test"}'
```

### 6.3 Monitoramento
1. Azure Monitor:
   - Acesse o portal Azure
   - Monitore métricas do Data Lake
   - Verifique logs do Event Grid

2. Pinecone Console:
   - Monitore uso do índice
   - Verifique métricas de queries

3. Redis Commander (opcional):
```bash
npm install -g redis-commander
redis-commander
# Acesse http://localhost:8081
```

## 7. Troubleshooting

### 7.1 Logs
- Backend: `backend/logs/app.log`
- Azure: Portal Azure > Monitor > Logs
- Pinecone: Console > Logs
- Redis: Redis Commander ou `docker logs redis`

### 7.2 Problemas Comuns
1. Erro de conexão com Pinecone:
   - Verifique API key e environment
   - Confirme se o índice existe
   - Verifique dimensão dos embeddings

2. Erro no Azure Data Lake:
   - Verifique permissões da storage account
   - Confirme se o container existe
   - Teste connection string

3. Cache não funciona:
   - Verifique se Redis está rodando
   - Teste conexão com redis-cli
   - Verifique configurações de porta