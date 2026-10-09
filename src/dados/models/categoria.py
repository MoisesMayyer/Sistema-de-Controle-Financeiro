from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from dados.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    valor_inicial = Column(Float, default=0, nullable=False)
    valor_limite = Column(Float, nullable=False)

    # Relacionamento com transações
    transacoes = relationship("Transacao", back_populates="categoria")