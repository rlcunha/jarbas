flowchart TD
    A("fa:fa-user Usuário") -- Envia mensagem --> B("fab:fa-react Frontend")
    B -- Requisição HTTP --> C("fab:fa-python Backend")
    C --> D("fab:fa-database Vector DB Service") & E("fab:fa-cloud Data Lake Service")
    C <--> F("fab:fa-brain LLM Service")
    Z("fab:fa-microsoft Azure Services") -- Atualiza dados --> E
    E -- Atualiza --> D
    D -- Armazena/Consulta --> G[("fab:fa-shapes Embeddings")]
    E -- Armazena --> H[("fab:fa-file-alt Arquivos Brutos")]
    F -- Processa linguagem --> I[("fab:fa-robot Modelo LLM")]
    C -- Resposta --> B
    B -- Exibe resposta --> A
    I <--> G

    style A color:#FFFFFF, fill:#2962FF, stroke:#2962FF
    style B color:#FFFFFF, fill:#61DAFB, stroke:#61DAFB
    style C color:#FFFFFF, fill:#3776AB, stroke:#3776AB
    style D color:#FFFFFF, fill:#FF6F61, stroke:#FF6F61
    style E color:#FFFFFF, fill:#00C853, stroke:#00C853
    style F color:#FFFFFF, fill:#AA00FF, stroke:#AA00FF
    style Z color:#FFFFFF, fill:#0078D4, stroke:#0078D4