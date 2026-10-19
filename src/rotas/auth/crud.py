from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from dados.dependencies import get_db, verificar_token
from dados.models import Usuario
from dados.schemas import Token
from dados.schemas.usuario import UsuarioResponse
from dados.security import criar_access_token, verificar_senha

router_auth = APIRouter(prefix="/auth", tags=["Autenticação"])


@router_auth.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not usuario.ativo:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_access_token({"sub": str(usuario.id)})

    return {"access_token": token, "token_type": "bearer"}


@router_auth.get("/me", response_model=UsuarioResponse)
def get_user(usuario: Usuario = Depends(verificar_token)):
    return usuario
