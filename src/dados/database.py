from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dados.config import settings

DATABASE_URL = settings.banco_dados

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)