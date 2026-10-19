from datetime import date
from pydantic import BaseModel, Field
from typing import Optional
from dados.models.transacao import TipoTransacao


class TransacaoBase(BaseModel):
    descricao: str = Field(..., min_length=1, max_length=255)
    valor: float = Field(..., gt=0)
    tipo: TipoTransacao
    data: date
    categoria_id: Optional[int] = None


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=1, max_length=255)
    valor: Optional[float] = Field(None, gt=0)
    tipo: Optional[TipoTransacao] = None
    data: Optional[date] = None
    categoria_id: Optional[int] = None


class TransacaoResponse(TransacaoBase):
    id: int
    usuario_id: int

    class Config:
        from_attributes = True