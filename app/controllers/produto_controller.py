# app/controllers/produto_controller.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import obter_usuario_autenticado
from app.domain.schemas import ProdutoCreate, ProdutoResponse
from app.repositories.produto_repository import ProdutoRepository
from app.services.produto_service import ProdutoService

controller = APIRouter(prefix="/produtos", tags=["Produtos"])

@controller.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar(produto_in: ProdutoCreate, db: Session = Depends(get_db), _u: str = Depends(obter_usuario_autenticado)):
    repo = ProdutoRepository(db)
    service = ProdutoService(repo)
    return service.criar_produto(produto_in)

@controller.get("/{id_produto}", response_model=ProdutoResponse)
def buscar_por_id(id_produto: int, db: Session = Depends(get_db)):
    repo = ProdutoRepository(db)
    service = ProdutoService(repo)
    return service.obter_por_id(id_produto)

@controller.get("/", response_model=List[ProdutoResponse])
def listar_todos(db: Session = Depends(get_db)):
    repo = ProdutoRepository(db)
    service = ProdutoService(repo)
    return service.listar_todos_produtos()

@controller.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(id_produto: int, db: Session = Depends(get_db), _u: str = Depends(obter_usuario_autenticado)):
    repo = ProdutoRepository(db)
    service = ProdutoService(repo)
    service.deletar_produto(id_produto)
    return None
