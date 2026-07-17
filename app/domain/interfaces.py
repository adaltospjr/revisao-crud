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


class ICache(ABC):
    @abstractmethod
    def definir(self, chave: str, valor: str, expiracao_segundos: int = 3600) -> None:
        pass

    @abstractmethod
    def buscar(self, chave: str) -> Optional[str]:
        pass

    @abstractmethod
    def deletar(self, chave: str) -> None:
        pass


class IEventPublisher(ABC):
    @abstractmethod
    def disparar_evento(self, topico: str, chave: str, payload: dict) -> None:
        pass
