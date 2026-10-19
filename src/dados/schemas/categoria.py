from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CategoriaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    valor_inicial: float = Field(default=0.0, ge=0)
    valor_limite: float = Field(..., gt=0)


class CategoriaCreate(CategoriaBase):
    @field_validator("valor_limite")
    @classmethod
    def limite_maior_que_inicial(cls, v, info):
        if "valor_inicial" in info.data and v <= info.data["valor_inicial"]:
            raise ValueError("valor_limite deve ser maior que valor_inicial")
        return v


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    valor_inicial: Optional[float] = Field(None, ge=0)
    valor_limite: Optional[float] = Field(None, gt=0)


class CategoriaResponse(CategoriaBase):
    id: int
    usuario_id: int
    total_despesas: float = Field(default=0.0, ge=0)
    total_receitas: float = Field(default=0.0, ge=0)
    saldo: float = 0.0
    porcentagem_limite: float = Field(default=0.0, ge=0, le=100)

    class Config:
        from_attributes = True