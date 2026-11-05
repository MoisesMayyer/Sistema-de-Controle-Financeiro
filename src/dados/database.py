from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dados.config import settings

DATABASE_URL = settings.database_url

engine = create_engine(
    DATABASE_URL,
    echo=False,
)

Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)