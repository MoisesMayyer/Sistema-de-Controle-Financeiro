from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, description="nome do usuario")
    email: EmailStr = Field(..., description="email do usuario")


class UsuarioCreate(UsuarioBase):
    senha: str = Field(...,min_length=6)

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("A senha não pode conter apenas espaços")

        return valor


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=100, description="nome do usuario")
    email: Optional[EmailStr] = Field(None, description="email do usuario")
    senha: Optional[str] = Field(None, min_length=6, description="senha do usuario")
    ativo: Optional[bool] = Field(None, description="ativo do usuario")


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    ativo: bool
    admin: bool

    class Config:
        from_attributes = True