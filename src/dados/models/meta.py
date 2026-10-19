from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from dados.database import Base


class Meta(Base):
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    valor_inicial = Column(Float, default=0, nullable=False)
    valor_final = Column(Float, nullable=False)
    data_inicio: date | None = Column(Date, nullable=True)  # type: ignore[assignment]
    data_fim: date | None = Column(Date, nullable=True)  # type: ignore[assignment]
    usuario_id: int = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)  # type: ignore[assignment]

    usuario = relationship("Usuario", back_populates="metas")