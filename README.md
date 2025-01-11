# Jarbas - Assistente Virtual Inteligente

Jarbas é um assistente virtual inteligente que combina tecnologias de ponta para fornecer respostas contextualizadas e interações naturais.

## Tecnologias Utilizadas

### Frontend
- Next.js 15.1.4
- React 18.3.1
- TypeScript 5.1.6
- Redux Toolkit
- Jest (testes)

### Backend
- Python 3.10
- FastAPI
- Uvicorn
- Docker

### Infraestrutura
- Docker Compose
- GitHub Actions (CI/CD)

## Como Configurar o Ambiente

### Pré-requisitos
- Node.js 18.x
- Python 3.10
- Docker
- Docker Compose

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/jarbas.git
cd jarbas
```

2. Instale as dependências do frontend:
```bash
cd frontend
npm install
```

3. Configure o backend:
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env.local` na raiz do projeto com as configurações necessárias.

## Como Executar

### Ambiente de Desenvolvimento

1. Inicie o backend:
```bash
cd backend
docker-compose up --build
```

2. Inicie o frontend:
```bash
cd ../frontend
npm run dev
```

A aplicação estará disponível em http://localhost:3000

## Estrutura de Diretórios

```
jarbas/
├── backend/          # Código do backend
├── frontend/         # Código do frontend
├── .github/          # Configurações do GitHub Actions
├── docker-compose.yml # Configuração do Docker Compose
└── README.md         # Este arquivo
```

## CI/CD

O projeto utiliza GitHub Actions para:
- Executar testes automatizados
- Verificar qualidade de código
- Fazer deploy automático

## Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

[MIT](https://choosealicense.com/licenses/mit/)