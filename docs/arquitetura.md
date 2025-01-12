flowchart TD
    A("fab:fa-react Frontend Next.js") -- HTTP --> B("fab:fa-python Backend Python")
    B --> C("fab:fa-database Vector DB") & D("fab:fa-cloud Data Lake") & E("fab:fa-brain LLM Service")
    D -- Atualiza --> C
    C --> F[("fab:fa-shapes Embeddings")]
    D --> G[("fab:fa-file-alt Arquivos Brutos")]
    E <--> H[("fab:fa-robot Modelos LLM")]
    H <--> F

    style A color:#FFFFFF, fill:#61DAFB, stroke:#61DAFB
    style B color:#FFFFFF, fill:#3776AB, stroke:#3776AB
    style C color:#FFFFFF, fill:#FF6F61, stroke:#FF6F61
    style D color:#FFFFFF, fill:#00C853, stroke:#00C853
    style E color:#FFFFFF, fill:#AA00FF, stroke:#AA00FF
