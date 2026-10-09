from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional
from dados.models.transacao import TipoTransacao


class TransacaoBase(BaseModel):
    descricao: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., gt=0, decimal_places=2)
    tipo: TipoTransacao
    data: date
    categoria_id: Optional[int] = None


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoUpdate(BaseModel):
    descricao: Optional[str] = Field(None, min_length=1, max_length=255)
    valor: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    tipo: Optional[TipoTransacao] = None
    data: Optional[date] = None
    categoria_id: Optional[int] = None


class TransacaoResponse(TransacaoBase):
    id: int

    class Config:
        from_attributes = True