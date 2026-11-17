import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from dados.config import settings
from dados.dependencies import get_db, verificar_token
from dados.limiter import LIMITE_GET, limiter
from dados.models import Usuario
from dados.schemas import RefreshRequest, Token
from dados.schemas.usuario import UsuarioResponse
from dados.security import criar_access_token, criar_refresh_token, verificar_senha

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

    return {
        "access_token": criar_access_token({"sub": str(usuario.id)}),
        "refresh_token": criar_refresh_token({"sub": str(usuario.id)}),
        "token_type": "bearer",
    }


@router_auth.post("/refresh", response_model=Token)
def refresh(dados: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            dados.refresh_token, settings.secret_key, algorithms=[settings.algorithm]
        )
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError
        usuario_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    return {
        "access_token": criar_access_token({"sub": str(usuario.id)}),
        "refresh_token": criar_refresh_token({"sub": str(usuario.id)}),
        "token_type": "bearer",
    }


@router_auth.get("/me", response_model=UsuarioResponse)
@limiter.limit(LIMITE_GET)
def get_user(request: Request, usuario: Usuario = Depends(verificar_token)):
    return usuario
