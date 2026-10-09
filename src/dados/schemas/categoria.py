from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    valor_inicial: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    valor_limite: Decimal = Field(..., gt=0, decimal_places=2)

    # Validação: limite deve ser maior que valor inicial
    @field_validator("valor_limite")
    @classmethod
    def limite_maior_que_inicial(cls, v, info):
        if "valor_inicial" in info.data and v <= info.data["valor_inicial"]:
            raise ValueError("valor_limite deve ser maior que valor_inicial")
        return v


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    valor_inicial: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    valor_limite: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True