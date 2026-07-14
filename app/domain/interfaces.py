from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.models import ProdutoModel, UserModel

class IUserRepository(ABC):
    @abstractmethod
    def buscar_por_username(self, username: str) -> Optional[UserModel]:
        pass

    @abstractmethod
    def criar_usuario(self, username: str, password_hash: str) -> UserModel:
        pass

class IProdutoRepository(ABC):
    @abstractmethod
    def criar(self, produto_model: ProdutoModel) -> ProdutoModel:
        pass

    @abstractmethod
    def buscar_por_id(self, id_produto: int) -> Optional[ProdutoModel]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[ProdutoModel]:
        pass

    @abstractmethod
    def deletar(self, id_produto: int) -> bool:
        pass
