import redis
from app.core.config import settings
from typing import Optional

class RedisCacheConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisCacheConnection, cls).__new__(cls)
            cls._instance.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
        return cls._instance

    def obter_cliente(self) -> redis.Redis:
        return self.client

    def definir(self, chave: str, valor: str, expiracao_segundos: int = 3600) -> None:
        self.client.set(name=chave, value=valor, ex=expiracao_segundos)

    def buscar(self, chave: str) -> Optional[str]:
        return self.client.get(chave)

    def deletar(self, chave: str) -> None:
        self.client.delete(chave)
