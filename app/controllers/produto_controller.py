from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.guards import autenticar_usuario
from app.domain.schemas import ProdutoCreate, ProdutoResponse
from app.repositories.produto_repository import ProdutoRepository
from app.services.produto_service import ProdutoService

controller = APIRouter(prefix="/produtos", tags=["Produtos"])


def get_produto_service(db: Session = Depends(get_db)) -> ProdutoService:
    return ProdutoService(repo=ProdutoRepository(db))


@controller.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar(
    produto_in: ProdutoCreate,
    service: ProdutoService = Depends(get_produto_service),
    _usuario_atual: str = Depends(autenticar_usuario),
):
    return service.criar_produto(produto_in)


@controller.get("/{id_produto}", response_model=ProdutoResponse)
def buscar_por_id(id_produto: int, service: ProdutoService = Depends(get_produto_service)):
    return service.obter_por_id(id_produto)


@controller.get("/", response_model=List[ProdutoResponse])
def listar_todos(service: ProdutoService = Depends(get_produto_service)):
    return service.listar_todos_produtos()


@controller.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    id_produto: int,
    service: ProdutoService = Depends(get_produto_service),
    _usuario_atual: str = Depends(autenticar_usuario),
):
    service.deletar_produto(id_produto)
    return None
