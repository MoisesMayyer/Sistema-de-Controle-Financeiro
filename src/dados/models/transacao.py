import enum
from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from dados.database import Base


class TipoTransacao(str, enum.Enum):
    RECEITA = "receita"
    DESPESA = "despesa"


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(255), nullable=False)
    valor = Column(Float, nullable=False)
    tipo: "TipoTransacao" = Column(SQLEnum(TipoTransacao), nullable=False)  # type: ignore
    data = Column(Date, nullable=False)  # type: ignore[assignment]
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    # Relacionamento com categoria
    categoria = relationship("Categoria", back_populates="transacoes")