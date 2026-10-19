from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from dados.config import settings

password_hash = PasswordHash.recommended()


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash Argon2 da senha."""
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash armazenado."""
    return password_hash.verify(senha, senha_hash)


def criar_access_token(dados: dict[str, object]) -> str:
    """Cria um token JWT com os dados informados e a expiração configurada."""
    payload = dados.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
