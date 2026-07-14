from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

Base = declarative_base()

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)

            cls._instance.engine = create_engine(
                settings.database_url,
                pool_pre_ping=True, # Testa a conexão antes de usar para evitar quedas
                pool_size=10, # Limite máximo de conexões simultâneas no pool
                max_overflow=20
            )

            cls._instance.SessionFactory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=cls._instance.engine
            )
        return cls._instance
    
    def get_session(self):
        return self.SessionFactory()

def get_db():
    db_singleton = DatabaseConnection()
    session = db_singleton.get_session()
    try:
        yield session
    finally:
        session.close()
