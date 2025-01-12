from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import chat_controller
from app.utils.config import settings
import uvicorn

app = FastAPI(
    title=settings.APP_NAME,
    description="API para integração com modelos de linguagem e geração de avatares",
    version="1.0.0",
    debug=settings.DEBUG_MODE,
    contact={
        "name": "Suporte",
        "email": "suporte@jarbas.com"
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[{
        "name": "chat",
        "description": "Operações relacionadas ao chat com avatar"
    }]
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar para ambientes específicos em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    chat_controller.router,
    prefix=settings.API_V1_STR,
    tags=["chat"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Jarbas API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )