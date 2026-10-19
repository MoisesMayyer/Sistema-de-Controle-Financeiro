from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from dados.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)

    categorias = relationship("Categoria", back_populates="usuario", cascade="all, delete-orphan")
    transacoes = relationship("Transacao", back_populates="usuario", cascade="all, delete-orphan")
    metas = relationship("Meta", back_populates="usuario", cascade="all, delete-orphan")
