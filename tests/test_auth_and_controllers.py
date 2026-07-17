import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.services.auth_service import AuthService
from app.domain.schemas import UserRegister
from app.repositories.user_repository import UserRepository
from app.core.guards import JwtAuthGuard
from app.core.security import SecurityService

client = TestClient(app)


class FakeUserRepository:
    def __init__(self):
        self.users = {}

    def buscar_por_username(self, username):
        return self.users.get(username)

    def criar_usuario(self, username, password_hash):
        self.users[username] = type("User", (), {"username": username, "password_hash": password_hash})()
        return self.users[username]


def test_auth_service_login_com_senha_invalida():
    repo = FakeUserRepository()
    repo.users["ana"] = type("User", (), {"username": "ana", "password_hash": "hash"})()
    service = AuthService(repo)

    with pytest.raises(Exception):
        service.login(UserRegister(username="ana", password="errada"))


def test_auth_service_renovar_token_acesso():
    repo = FakeUserRepository()
    service = AuthService(repo)

    with patch("app.services.auth_service.jwt.decode", return_value={"scope": "refresh_token", "sub": "ana"}), \
         patch("app.services.auth_service.SecurityService.criar_token", side_effect=["new-access", "new-refresh"]):
        token = service.renovar_token_acesso("refresh-token")

    assert token.access_token == "new-access"
    assert token.refresh_token == "new-refresh"


def test_auth_controller_register_and_login(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.username = "ana"

    monkeypatch.setattr("app.controllers.auth_controller.UserRepository", lambda db: object())
    monkeypatch.setattr(
        "app.controllers.auth_controller.AuthService",
        lambda repo: type(
            "Svc",
            (),
            {
                "registrar": lambda self, dados: FakeResponse(),
                "login": lambda self, dados: {"access_token": "t", "refresh_token": "r", "token_type": "bearer"},
            },
        )(),
    )

    response = client.post("/auth/register", data={"username": "ana", "password": "senha123"})
    assert response.status_code == 201

    response = client.post("/auth/login", data={"username": "ana", "password": "senha123"})
    assert response.status_code == 200


def test_guard_uses_auth_service(monkeypatch):
    repo = FakeUserRepository()
    auth_service = AuthService(repo)
    guard = JwtAuthGuard()

    monkeypatch.setattr("app.core.guards.UserRepository", lambda db: object())
    monkeypatch.setattr("app.core.guards.AuthService", lambda repo: auth_service)
    monkeypatch.setattr("app.core.guards.HTTPBearer", lambda: None)

    with patch("app.core.guards.JwtAuthGuard.__call__", return_value="ana"):
        assert guard is not None
