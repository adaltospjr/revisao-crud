from pydantic import BaseModel, Field
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenInput(BaseModel):
    refresh_token: str

class ProdutoBase(BaseModel):
    nome: str
    preco: float
    descricao: Optional[str] = None

class ProdutoCreate(ProdutoBase):
    id: int

class ProdutoResponse(ProdutoBase):
    id: int
    model_config = {"from_attributes": True}
