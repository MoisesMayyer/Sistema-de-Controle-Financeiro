from datetime import date
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class MetaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    valor_inicial: float = Field(default=0.0, ge=0)
    valor_final: float = Field(..., gt=0)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    @field_validator("valor_final")
    @classmethod
    def final_maior_que_inicial(cls, v, info):
        if "valor_inicial" in info.data and v <= info.data["valor_inicial"]:
            raise ValueError("valor_final deve ser maior que valor_inicial")
        return v

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
    valor_inicial: Optional[float] = Field(None, ge=0)
    valor_final: Optional[float] = Field(None, gt=0)
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None


class MetaResponse(MetaBase):
    id: int
    porcentagem: float = Field(default=0.0, ge=0, le=100)

    class Config:
        from_attributes = True