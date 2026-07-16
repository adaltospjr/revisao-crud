from datetime import timedelta
import jwt
from fastapi import HTTPException, status
from app.domain.interfaces import IUserRepository
from app.domain.schemas import UserRegister, Token
from app.core.security import SecurityService
from app.core.config import settings

class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.repo = user_repository

    def registrar(self, dados: UserRegister):
        usuario_existente = self.repo.buscar_por_username(dados.username)
        if usuario_existente:
            raise HTTPException(status_code=400, detail="Este nome de usuário já está cadastrado.")
        hash_senha = SecurityService.gerar_hash_senha(dados.password)
        return self.repo.criar_usuario(dados.username, hash_senha)

    def login(self, dados: UserRegister) -> Token:
        usuario = self.repo.buscar_por_username(dados.username)
        if not usuario or not SecurityService.verificar_senha(dados.password, usuario.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário ou senha incorretos.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_acesso = SecurityService.criar_token(
            dados={"sub": usuario.username},
            escopo="access_token",
            tempo_expiracao=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        token_renovacao = SecurityService.criar_token(
            dados={"sub": usuario.username},
            escopo="refresh_token",
            tempo_expiracao=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return Token(access_token=token_acesso, refresh_token=token_renovacao, token_type="bearer")

    def validar_token_acesso(self, token: str) -> str:
        """Decodifica o token e valida no banco se o usuário realmente existe."""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            
            if payload.get("scope") != "access_token":
                raise HTTPException(status_code=401, detail="Token inválido para esta operação")
                
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Token inválido: Usuário ausente")
                
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Token expirado (5 min) ou inválido.")

        usuario_valido = self.repo.buscar_por_username(username)
        if not usuario_valido:
            raise HTTPException(status_code=401, detail="Acesso negado: Usuário inexistente na base.")
            
        return username

    def renovar_token_acesso(self, refresh_token: str) -> Token:
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("scope") != "refresh_token":
                raise HTTPException(status_code=401, detail="Token inválido")
            username: str = payload.get("sub")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Refresh Token expirado ou corrompido.")

        novo_access_token = SecurityService.criar_token(
            dados={"sub": username}, escopo="access_token", tempo_expiracao=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        novo_refresh_token = SecurityService.criar_token(
            dados={"sub": username}, escopo="refresh_token", tempo_expiracao=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return Token(access_token=novo_access_token, refresh_token=novo_refresh_token, token_type="bearer")
