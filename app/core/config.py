# app/core/config.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str = Field(..., description="Usuário do banco de dados, obrigatório via .env")
    DB_PASSWORD: str = Field(..., description="Senha do banco de dados, obrigatória via .env")
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "catalogo_prod_db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    JWT_SECRET_KEY: str = Field(..., description="Chave secreta do JWT, obrigatória via .env")
    JWT_ALGORITHM: str = "HS256"
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
