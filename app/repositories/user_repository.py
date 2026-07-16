from typing import Optional
from sqlalchemy.orm import Session
from app.domain.models import UserModel
from app.domain.interfaces import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def buscar_por_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def criar_usuario(self, username: str, password_hash: str) -> UserModel:
        novo_usuario = UserModel(username=username, password_hash=password_hash)
        self.db.add(novo_usuario)
        self.db.commit()
        self.db.refresh(novo_usuario)
        return novo_usuario
