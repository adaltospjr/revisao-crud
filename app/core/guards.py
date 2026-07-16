from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

class JwtAuthGuard:
    def __init__(self):
        self.security_scheme = HTTPBearer()

    def __call__(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        db: Session = Depends(get_db)
    ) -> str:
        token = credentials.credentials
        
        repo = UserRepository(db)
        auth_service = AuthService(repo)
        username = auth_service.validar_token_acesso(token)
        return username

autenticar_usuario = JwtAuthGuard()
