import json

import pytest
from fastapi import HTTPException

from app.domain.models import ProdutoModel
from app.domain.schemas import ProdutoCreate
from app.services.produto_service import ProdutoService
from app.use_cases.produto_use_cases import CriarProdutoUseCase


class FakeProdutoRepository:
    def __init__(self):
        self._produtos = {}
        self.criados = []

    def criar(self, produto_model: ProdutoModel) -> ProdutoModel:
        self._produtos[produto_model.id] = produto_model
        self.criados.append(produto_model)
        return produto_model

    def buscar_por_id(self, id_produto: int):
        return self._produtos.get(id_produto)

    def listar_todos(self):
        return list(self._produtos.values())

    def deletar(self, id_produto: int) -> bool:
        if id_produto in self._produtos:
            del self._produtos[id_produto]
            return True
        return False


class FakeCache:
    def __init__(self):
        self.itens = {}

    def definir(self, chave: str, valor: str, expiracao_segundos: int = 3600) -> None:
        self.itens[chave] = {"valor": valor, "expiracao_segundos": expiracao_segundos}

    def buscar(self, chave: str):
        item = self.itens.get(chave)
        return item["valor"] if item else None

    def deletar(self, chave: str) -> None:
        self.itens.pop(chave, None)


class FakeEventPublisher:
    def __init__(self):
        self.eventos = []

    def disparar_evento(self, topico: str, chave: str, payload: dict) -> None:
        self.eventos.append({"topico": topico, "chave": chave, "payload": payload})


def test_criar_produto_salva_no_repositorio_e_publica_evento():
    repo = FakeProdutoRepository()
    cache = FakeCache()
    publisher = FakeEventPublisher()
    service = ProdutoService(repo=repo, cache=cache, event_publisher=publisher)

    produto = service.criar_produto(
        ProdutoCreate(id=1, nome="Notebook", preco=4999.9, descricao="Bom")
    )

    assert produto.id == 1
    assert repo.criados[0].nome == "Notebook"
    assert json.loads(cache.buscar("produto:1"))["nome"] == "Notebook"
    assert publisher.eventos[0]["payload"]["evento"] == "PRODUTO_CRIADO"


def test_caso_de_uso_criar_produto_executa_fluxo_basico():
    repo = FakeProdutoRepository()
    cache = FakeCache()
    publisher = FakeEventPublisher()
    use_case = CriarProdutoUseCase(repo=repo, cache=cache, event_publisher=publisher)

    produto = use_case.executar(
        ProdutoCreate(id=2, nome="Teclado", preco=199.9, descricao="Mecânico")
    )

    assert produto.id == 2
    assert repo.buscar_por_id(2).nome == "Teclado"
    assert json.loads(cache.buscar("produto:2"))["nome"] == "Teclado"
    assert publisher.eventos[0]["payload"]["evento"] == "PRODUTO_CRIADO"


def test_service_obter_por_id_usando_cache_e_busca_no_repositorio():
    repo = FakeProdutoRepository()
    cache = FakeCache()
    publisher = FakeEventPublisher()
    service = ProdutoService(repo=repo, cache=cache, event_publisher=publisher)

    repo.criar(ProdutoModel(id=3, nome="Mouse", preco=80.0, descricao="Óptico"))
    produto = service.obter_por_id(3)

    assert produto.id == 3
    assert json.loads(cache.buscar("produto:3"))["nome"] == "Mouse"


def test_service_deletar_produto_publica_evento_e_remove_cache():
    repo = FakeProdutoRepository()
    cache = FakeCache()
    publisher = FakeEventPublisher()
    service = ProdutoService(repo=repo, cache=cache, event_publisher=publisher)

    repo.criar(ProdutoModel(id=4, nome="Monitor", preco=500.0, descricao="Full HD"))
    cache.definir("produto:4", "{}")

    service.deletar_produto(4)

    assert repo.buscar_por_id(4) is None
    assert cache.buscar("produto:4") is None
    assert publisher.eventos[-1]["payload"]["evento"] == "PRODUTO_DELETADO"


def test_caso_de_uso_criar_produto_lanca_erro_quando_duplicado():
    repo = FakeProdutoRepository()
    repo.criar(ProdutoModel(id=5, nome="Câmera", preco=1000.0, descricao="Boa"))
    use_case = CriarProdutoUseCase(repo=repo)

    with pytest.raises(HTTPException):
        use_case.executar(ProdutoCreate(id=5, nome="Câmera", preco=1000.0, descricao="Boa"))
