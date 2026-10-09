from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class MetaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    valor_inicial: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    valor_final: Decimal = Field(..., gt=0, decimal_places=2)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    # Validação: valor_final deve ser maior que valor_inicial
    @field_validator("valor_final")
    @classmethod
    def final_maior_que_inicial(cls, v, info):
        if "valor_inicial" in info.data and v <= info.data["valor_inicial"]:
            raise ValueError("valor_final deve ser maior que valor_inicial")
        return v

    # Validação: data_fim deve ser posterior a data_inicio
    @field_validator("data_fim")
    @classmethod
    def fim_depois_inicio(cls, v, info):
        if v and "data_inicio" in info.data and info.data["data_inicio"] and v <= info.data["data_inicio"]:
            raise ValueError("data_fim deve ser posterior a data_inicio")
        return v


class MetaCreate(MetaBase):
    pass


class MetaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    valor_inicial: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    valor_final: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None


class MetaResponse(MetaBase):
    id: int
    porcentagem: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    class Config:
        from_attributes = True