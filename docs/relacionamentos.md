erDiagram
    %% Entities
    FRONTEND {
        string name "Frontend Next.js"
    }
    BACKEND {
        string name "Backend Python"
    }
    VECTOR_DB {
        string name "Vector DB"
    }
    DATA_LAKE {
        string name "Data Lake"
    }
    LLM {
        string name "LLM Service"
    }
    TESTES_INTEGRACAO {
        string name "Testes de Integração"
    }

    %% Relationships
    AZURE ||--o{ DATA_LAKE : "Sincroniza"
    FRONTEND ||--o{ BACKEND : "Requisições HTTP"
    LLM ||--o{ VECTOR_DB : "Armazena/Consulta Embeddings"
    BACKEND ||--o{ DATA_LAKE : "Armazena Dados Brutos"
    DATA_LAKE ||--o{ VECTOR_DB : "Atualiza Dados"
    BACKEND ||--o{ LLM : "Processa Linguagem Natural"
    TESTES_INTEGRACAO ||--o{ BACKEND : "Verifica Integração"
    TESTES_INTEGRACAO ||--o{ VECTOR_DB : "Verifica Integração"
    TESTES_INTEGRACAO ||--o{ DATA_LAKE : "Verifica Integração"
    TESTES_INTEGRACAO ||--o{ LLM : "Verifica Integração"

    %% Notes
    %% Data Lake atualiza Vector DB com novos dados
    %% Vector DB armazena representações vetoriais