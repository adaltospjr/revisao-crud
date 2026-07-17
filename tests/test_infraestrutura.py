from types import SimpleNamespace

import pytest
from unittest.mock import Mock

from app.core.cache import RedisCacheConnection
from app.core.queue import KafkaProducerConnection
from app.repositories.produto_repository import ProdutoRepository
from app.domain.models import ProdutoModel
from app.services.auth_service import AuthService
from app.domain.schemas import UserRegister, Token
from app.core.security import SecurityService
from app.core.database import DatabaseConnection, get_db
from app.controllers.produto_controller import get_produto_service


class FakeDbSession:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.committed = 0
        self.refreshed = []
        self._produtos = {}

    def add(self, obj):
        self.added.append(obj)
        self._produtos[obj.id] = obj

    def commit(self):
        self.committed += 1

    def refresh(self, obj):
        self.refreshed.append(obj)

    def query(self, model):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return next(iter(self._produtos.values()), None)

    def all(self):
        return list(self._produtos.values())

    def delete(self, obj):
        self.deleted.append(obj)
        self._produtos.pop(obj.id, None)


class FakeUserRepository:
    def __init__(self):
        self.usuario = None

    def buscar_por_username(self, username):
        return self.usuario if self.usuario and self.usuario.username == username else None

    def criar_usuario(self, username, password_hash):
        self.usuario = SimpleNamespace(username=username, password_hash=password_hash)
        return self.usuario


def test_redis_cache_connection_methods(monkeypatch):
    client = Mock()
    monkeypatch.setattr("app.core.cache.redis.Redis", lambda *args, **kwargs: client)
    cache = RedisCacheConnection()
    cache.definir("x", "1", expiracao_segundos=10)
    cache.buscar("x")
    cache.deletar("x")
    assert client.set.called
    assert client.get.called
    assert client.delete.called


def test_kafka_producer_connection_disparar_evento(monkeypatch):
    producer = Mock()
    monkeypatch.setattr("app.core.queue.Producer", lambda config: producer)
    queue = KafkaProducerConnection()
    queue.disparar_evento("topico", "1", {"evento": "ok"})
    assert producer.produce.called
    assert producer.flush.called


def test_produto_repository_criar_e_deletar():
    session = FakeDbSession()
    repo = ProdutoRepository(session)
    produto = ProdutoModel(id=1, nome="A", preco=10.0, descricao="B")
    repo.criar(produto)
    repo.buscar_por_id(1)
    repo.listar_todos()
    assert repo.deletar(1) is True


def test_auth_service_registrar_e_login(monkeypatch):
    repo = FakeUserRepository()
    service = AuthService(repo)

    usuario = service.registrar(UserRegister(username="ana", password="senha123"))
    assert usuario.username == "ana"

    token = service.login(UserRegister(username="ana", password="senha123"))
    assert token.access_token
    assert token.refresh_token


def test_auth_service_validar_token_acesso_erro_e_sucesso(monkeypatch):
    repo = FakeUserRepository()
    service = AuthService(repo)

    with pytest.raises(Exception):
        service.validar_token_acesso("token-invalido")

    repo.usuario = SimpleNamespace(username="ana", password_hash="hash")
    monkeypatch.setattr("app.services.auth_service.SecurityService.criar_token", lambda **kwargs: "token")
    monkeypatch.setattr("app.services.auth_service.jwt.decode", lambda *args, **kwargs: {"scope": "access_token", "sub": "ana"})
    assert service.validar_token_acesso("token") == "ana"


def test_security_service_helpers():
    senha_hash = SecurityService.gerar_hash_senha("senha123")
    assert SecurityService.verificar_senha("senha123", senha_hash) is True
    assert SecurityService.verificar_senha("errada", senha_hash) is False


def test_database_connection_singleton_and_get_db(monkeypatch):
    class FakeSession:
        def close(self):
            self.closed = True

    fake_session = FakeSession()
    fake_session.closed = False
    monkeypatch.setattr("app.core.database.create_engine", lambda *args, **kwargs: object())
    monkeypatch.setattr("app.core.database.sessionmaker", lambda *args, **kwargs: lambda: fake_session)

    DatabaseConnection._instance = None
    connection = DatabaseConnection()
    assert connection.get_session() is not None

    gen = get_db()
    next(gen)
    with pytest.raises(StopIteration):
        next(gen)


def test_get_produto_service_uses_repository(monkeypatch):
    db = object()
    monkeypatch.setattr("app.controllers.produto_controller.get_db", lambda: iter([db]))
    service = get_produto_service(db)
    assert service is not None
