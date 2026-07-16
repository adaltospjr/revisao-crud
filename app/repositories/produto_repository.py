from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models import ProdutoModel
from app.domain.interfaces import IProdutoRepository

class ProdutoRepository(IProdutoRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def criar(self, produto_model: ProdutoModel) -> ProdutoModel:
        self.db.add(produto_model)
        self.db.commit()
        self.db.refresh(produto_model)
        return produto_model

    def buscar_por_id(self, id_produto: int) -> Optional[ProdutoModel]:
        return self.db.query(ProdutoModel).filter(ProdutoModel.id == id_produto).first()

    def listar_todos(self) -> List[ProdutoModel]:
        return self.db.query(ProdutoModel).all()

    def deletar(self, id_produto: int) -> bool:
        produto = self.buscar_por_id(id_produto)
        if produto:
            self.db.delete(produto)
            self.db.commit()
            return True
        return False
