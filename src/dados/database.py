from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexão com SQLite
DATABASE_URL = "sqlite:///./financeiro.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Necessário para SQLite
    echo=False,
)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)