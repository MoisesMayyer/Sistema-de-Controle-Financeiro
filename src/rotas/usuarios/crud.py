from fastapi import APIRouter

from dados.models import Usuario

router_usuario = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router_usuario.get("/")
def listar_usuarios():
    pass


@router_usuario.get("/{id}")
def buscar_usuario(id: int):
    pass


@router_usuario.post("/")
def criar_usuario():
    pass


@router_usuario.put("/{id}")
def editar_usuario(id: int):
    pass


@router_usuario.patch("/{id}/cancelar")
def cancelar_usuario(id: int):
    pass


@router_usuario.delete("/{id}")
def remover_usuario(id: int):
    pass
