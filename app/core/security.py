from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security_scheme = HTTPBearer()

class SecurityService:
    @staticmethod
    def verificar_senha(senha_pura: str, senha_hashed: str) -> bool:
        try:
            return bcrypt.checkpw(senha_pura.encode('utf-8'), senha_hashed.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def gerar_hash_senha(senha_pura: str) -> str:
        return bcrypt.hashpw(senha_pura.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def criar_token(dados: dict, escopo: str, tempo_expiracao: timedelta) -> str:
        dados_copia = dados.copy()
        expiracao = datetime.now(timezone.utc) + tempo_expiracao
        dados_copia.update({"exp": expiracao, "scope": escopo})
        return jwt.encode(dados_copia, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
