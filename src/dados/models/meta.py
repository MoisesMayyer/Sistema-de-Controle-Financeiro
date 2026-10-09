from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date
from dados.database import Base


class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    valor_inicial = Column(Float, default=0, nullable=False)
    valor_final = Column(Float, nullable=False)
    data_inicio = Column(Date, nullable=True)  # type: ignore[assignment]
    data_fim = Column(Date, nullable=True)  # type: ignore[assignment]