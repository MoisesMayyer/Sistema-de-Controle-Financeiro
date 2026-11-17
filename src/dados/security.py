from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from dados.config import settings

password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def _criar_token(dados: dict[str, object], tipo: str, minutos: int) -> str:
    payload = dados.copy()
    payload["type"] = tipo
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def criar_access_token(dados: dict[str, object]) -> str:
    return _criar_token(dados, "access", settings.access_token_expire_minutes)


def criar_refresh_token(dados: dict[str, object]) -> str:
    return _criar_token(
        dados, "refresh", settings.refresh_token_expire_days * 24 * 60
    )
