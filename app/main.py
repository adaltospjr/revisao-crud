# app/main.py
from fastapi import FastAPI
from app.core.database import DatabaseConnection, Base

# Importações separadas e diretas para evitar conflitos de módulo
import app.controllers.auth_controller as auth_controller
import app.controllers.produto_controller as produto_controller

app = FastAPI(
    title="API de Catálogo de Produtos Enterprise",
    description="API com arquitetura baseada em Controllers, Autenticação JWT com expiração curta e Refresh Token.",
    version="1.1.0"
)

@app.on_event("startup")
def on_startup():
    db = DatabaseConnection()
    Base.metadata.create_all(bind=db.engine)

app.include_router(auth_controller.controller)
app.include_router(produto_controller.controller)

@app.get("/", tags=["Home"])
def read_root():
    return {"mensagem": "API ativa! Acesse /docs para testar as rotas de Refresh Token de 5 minutos."}
