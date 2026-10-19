from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dados.dependencies import get_db, verificar_token
from dados.models import Usuario
from dados.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from dados.security import gerar_hash_senha

router_usuario = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router_usuario.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    if usuario.admin:
        return db.query(Usuario).all()

    return [usuario]


@router_usuario.get("/{id}", response_model=UsuarioResponse)
def buscar_usuario(
    id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    if usuario.id != id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Sem permissão")

    alvo = db.query(Usuario).filter(Usuario.id == id).first()

    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return alvo


@router_usuario.post("/", response_model=UsuarioResponse, status_code=201)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existe = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if usuario_existe:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = gerar_hash_senha(dados.senha)

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=senha_hash,
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router_usuario.put("/{id}", response_model=UsuarioResponse)
def editar_usuario(
    id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    alvo = db.query(Usuario).filter(Usuario.id == id).first()

    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.id != alvo.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Sem permissão")

    if dados.nome is not None:
        alvo.nome = dados.nome

    if dados.email is not None:
        email_existe = (
            db.query(Usuario)
            .filter(Usuario.email == dados.email, Usuario.id != id)
            .first()
        )
        if email_existe:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        alvo.email = dados.email

    if dados.senha is not None:
        alvo.senha_hash = gerar_hash_senha(dados.senha)

    if dados.ativo is not None:
        if not usuario.admin:
            raise HTTPException(status_code=403, detail="Apenas administradores")
        alvo.ativo = dados.ativo

    db.commit()
    db.refresh(alvo)
    return alvo


@router_usuario.patch("/{id}/cancelar", response_model=UsuarioResponse)
def cancelar_usuario(
    id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    alvo = db.query(Usuario).filter(Usuario.id == id).first()

    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.id != alvo.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Sem permissão")

    alvo.ativo = False
    db.commit()
    db.refresh(alvo)

    return alvo


@router_usuario.delete("/{id}", status_code=204)
def remover_usuario(
    id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    alvo = db.query(Usuario).filter(Usuario.id == id).first()

    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if usuario.id != alvo.id and not usuario.admin:
        raise HTTPException(status_code=403, detail="Sem permissão")

    db.delete(alvo)
    db.commit()
