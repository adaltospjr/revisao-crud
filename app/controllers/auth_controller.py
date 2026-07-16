# app/controllers/auth_controller.py
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domain.schemas import UserRegister, Token, RefreshTokenInput
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

controller = APIRouter(prefix="/auth", tags=["Autenticação"])

@controller.post("/register", status_code=status.HTTP_201_CREATED, summary="Cadastrar um novo usuário")
def registrar_usuario(dados: UserRegister, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    usuario = service.registrar(dados)
    return {"status": "sucesso", "username": usuario.username}

@controller.post("/login", response_model=Token, summary="Efetuar login seguro com senha mascarada")
def login_usuario(
    dados: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    service = AuthService(repo)
    dados_adaptados = UserRegister(username=dados.username, password=dados.password)
    return service.login(dados_adaptados)

@controller.post("/refresh", response_model=Token, summary="Gera um novo token caso o de 5 minutos expire")
def renovar_token(dados: RefreshTokenInput, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    service = AuthService(repo)
    return service.renovar_token_acesso(dados.refresh_token)
