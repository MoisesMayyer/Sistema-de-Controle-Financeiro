from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

from dados.config import settings
from dados.database import SessionLocal
from dados.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verificar_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        usuario_id = payload.get("sub")

        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Acesso negado")

        try:
            usuario_id = int(usuario_id)
        except (ValueError, TypeError):
            raise HTTPException(status_code=401, detail="Acesso negado")

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Acesso negado")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso negado")

    if not usuario.ativo:
        raise HTTPException(status_code=401, detail="Acesso negado")

    return usuario
