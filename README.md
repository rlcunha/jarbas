# Jarbas - Assistente Virtual com IA

Sistema de assistente virtual baseado em IA com processamento de linguagem natural, banco de dados vetorial e integração com Azure.

## Guia Rápido

### Configuração Rápida

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/jarbas.git
cd jarbas
```

2. Configure as credenciais (veja [SETUP.md](SETUP.md) para instruções detalhadas)
```bash
cp backend/.env.example backend/.env
# Edite .env com suas credenciais:
# - OpenAI API Key
# - Azure Storage Account
# - Pinecone API Key
# - Redis connection
```

3. Instale dependências e execute
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Redis
docker-compose up redis
```

Para instruções detalhadas de configuração de cada componente, incluindo:
- Como obter todas as credenciais necessárias
- Passo a passo de configuração de cada serviço
- Troubleshooting e monitoramento

➡️ Consulte o guia completo em [SETUP.md](SETUP.md)

## Arquitetura

### Stack Tecnológica

#### 1. Infraestrutura
- **Azure Data Lake Storage**: Armazenamento de dados brutos
  - Documentos, arquivos JSON, CSV, etc.
  - Integração com Azure Event Grid para eventos em tempo real

#### 2. Banco Vetorial
- **Pinecone**: Banco de dados vetorial gerenciado
  - Armazenamento e busca eficiente de embeddings
  - Alta performance para consultas de similaridade

#### 3. LLM (Large Language Model)
- **OpenAI GPT**: Modelo principal para geração de respostas
  - Integração via API OpenAI
  - Suporte a diferentes modelos (GPT-3.5-turbo, GPT-4)

#### 4. Pipeline de Ingestão
- **LangChain**: Framework para integração com LLMs
  - Geração de embeddings
  - Consultas contextuais
  - Templates de prompts

#### 5. Frontend
- **Next.js**: Interface web moderna
  - Renderização no servidor (SSR)
  - APIs integradas
- **TailwindCSS**: Estilização responsiva

#### 6. Cache e Performance
- **Redis**: Cache de respostas
  - Redução de chamadas ao LLM
  - Melhoria de performance

## Endpoints da API

### 1. Chat com LLM Direto

```http
POST /api/v1/ask
Content-Type: application/json

{
  "question": "Qual é a capital da França?",
  "user_id": "optional-user-id"
}
```

Resposta:
```json
{
  "question": "Qual é a capital da França?",
  "text_response": {
    "text": "A capital da França é Paris.",
    "confidence": 0.95
  },
  "avatar_response": {
    "avatar_url": "http://localhost:8000/audio/response.wav",
    "animation_data": {
      "duration": 5.2
    }
  },
  "timestamp": "2025-01-10T23:11:04.156558",
  "cache_hit": false
}
```

### 2. Chat com Banco Vetorial

```http
POST /api/v1/vector-ask
Content-Type: application/json

{
  "question": "O que é machine learning?",
  "user_id": "optional-user-id"
}
```

Resposta:
```json
{
  "question": "O que é machine learning?",
  "text_response": {
    "text": "Machine Learning é um ramo da IA...",
    "confidence": 0.95
  },
  "context": [
    "Machine Learning é uma tecnologia que permite...",
    "Exemplos de aplicações incluem..."
  ],
  "sources": [
    "docs/ml_intro.pdf",
    "docs/ai_examples.txt"
  ],
  "avatar_response": {
    "avatar_url": "http://localhost:8000/audio/response.wav",
    "animation_data": {
      "duration": 5.2
    }
  },
  "timestamp": "2025-01-10T23:11:04.156558",
  "cache_hit": false
}
```

## Fluxo de Dados

### 1. Ingestão de Documentos
```
[Azure Data Lake] -> [Event Grid] -> [Processamento] -> [Pinecone]
```
- Novos documentos são detectados pelo Event Grid
- Documentos são processados e convertidos em embeddings
- Embeddings são armazenados no Pinecone

### 2. Consultas do Usuário
```
[Frontend] -> [API] -> [Vector Search] -> [LLM] -> [Resposta]
```
- Usuário faz pergunta via frontend
- API busca contexto relevante no banco vetorial
- LLM gera resposta baseada no contexto
- Resposta é cacheada e retornada ao usuário

## Testes

O projeto inclui uma suíte completa de testes para validar todos os componentes da stack.

### 1. Testes Unitários

Testes isolados para cada serviço:

```bash
# Executa todos os testes unitários
pytest backend/tests/test_services/

# Testes específicos
pytest backend/tests/test_services/test_vector_db_service.py
pytest backend/tests/test_services/test_data_lake_service.py
pytest backend/tests/test_services/test_vector_llm_service.py
```

### 2. Testes de Integração

Testes do fluxo completo da stack:

```bash
# Executa testes de integração
pytest backend/tests/test_integration/test_stack_integration.py -m integration
```

## Desenvolvimento

### Estrutura do Projeto
```
jarbas/
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   │       └── config.py  # Gerenciamento centralizado de configurações
│   ├── tests/
│   │   ├── test_services/     # Testes unitários
│   │   └── test_integration/  # Testes de integração
│   └── main.py
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── services/
    └── public/
```

### Principais Serviços

- **DataLakeService**: Integração com Azure Data Lake
- **VectorDBService**: Gerenciamento do banco vetorial
- **VectorLLMService**: Integração LLM + Banco Vetorial
- **CacheService**: Gerenciamento de cache

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
