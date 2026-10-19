from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from dados.database import Base


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("usuario_id", "nome", name="uq_categorias_usuario_nome"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    valor_inicial = Column(Float, default=0, nullable=False)
    valor_limite = Column(Float, nullable=False)
    usuario_id: int = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)  # type: ignore[assignment]

    usuario = relationship("Usuario", back_populates="categorias")
    transacoes = relationship("Transacao", back_populates="categoria")