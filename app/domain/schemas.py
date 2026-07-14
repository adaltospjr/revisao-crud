from pydantic import BaseModel, Field
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_lenght=3, max_lenght=50)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str

class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    preco: float = Field(..., gt=0, description="O preço precisa ser maior que zero")
    descricao: Optional[str] = Field(None, max_length=255)

class ProdutoCreate(ProdutoBase):
    id: int = Field(..., gt=0, description="ID único para indexação na Árvore Binária")

class ProdutoResponse(ProdutoBase):
    id: int

    # configuração para o Pydantic conseguir ler objetos nativos do SQLAlchemy ORM
    model_config = {"from_attributes": True}
