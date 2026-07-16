from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class UserModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True) 
    nome = Column(String(100), nullable=False)
    preco = Column(Float, nullable=False)
    descricao = Column(String(255), nullable=True)
