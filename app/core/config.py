# app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configurações do Banco de Dados Postgres (Sem valores padrão para dados sensíveis)
    DB_USER: str = Field(..., description="Usuário do banco de dados, obrigatório via .env")
    DB_PASSWORD: str = Field(..., description="Senha do banco de dados, obrigatória via .env")
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "catalogo_prod_db"

    # Configurações do Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Configurações do Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # Segurança & JWT (Chave secreta obrigatoriamente externa em produção)
    JWT_SECRET_KEY: str = Field(..., description="Chave secreta do JWT, obrigatória via .env")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def database_url(self) -> str:
        """Monta a URL de conexão do SQLAlchemy dinamicamente."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Configuração para ler estritamente do arquivo .env localizado na raiz
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instancia globalmente. Se o arquivo .env estiver incompleto, um erro será disparado aqui.
settings = Settings()
