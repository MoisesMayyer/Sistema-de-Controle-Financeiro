from datetime import datetime, timedelta, timezone

import jwt
import pytest

from dados.config import settings


def _criar_token(payload: dict) -> str:
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def test_login_senha_invalida(client, usuario):
    resposta = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "senhainvalida"},
    )

    assert resposta.status_code == 401, resposta.text


def test_login_email_invalido(client):
    resposta = client.post(
        "/auth/login",
        data={"username": "email@errado.com", "password": "senha12345"}
    )

    assert resposta.status_code == 401, resposta.text


@pytest.mark.parametrize(
    ("email", "senha"),
    [
        ("user1@example.com", ""),
        ("", "senha12345"),
        ("", ""),
    ]
)
def test_login_dados_vazios(client, usuario, email, senha):
    resposta = client.post(
        "/auth/login",
        data={"username": email, "password": senha},
    )

    assert resposta.status_code == 422, resposta.text


def test_login_valido(client, usuario):
    resposta = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "senha12345"},
    )

    assert resposta.status_code == 200, resposta.text

    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]

    autenticado = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {corpo['access_token']}"},
    )

    assert autenticado.status_code == 200, autenticado.text
    assert autenticado.json()["email"] == usuario["email"]


def test_login_conta_desativada(client, criar_usuario):
    criar_usuario(nome="ana", email="ana@example.com", senha="senha123", ativo=False)

    resposta = client.post(
        "/auth/login",
        data={"username": "ana@example.com", "password": "senha123"},
    )

    assert resposta.status_code == 401, resposta.text


def test_me_retorna_usuario_autenticado(client, usuario, headers):
    resposta = client.get("/auth/me", headers=headers)

    assert resposta.status_code == 200, resposta.text

    corpo = resposta.json()
    assert corpo["id"] == usuario["id"]
    assert corpo["email"] == usuario["email"]
    assert "senha_hash" not in corpo


def test_me_sem_token(client):
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401, resposta.text


def test_me_token_invalido(client):
    resposta = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer token.invalido.aqui"},
    )

    assert resposta.status_code == 401, resposta.text


def test_me_token_expirado(client, usuario):
    token = _criar_token(
        {
            "sub": str(usuario["id"]),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
    )

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401, resposta.text


def test_me_token_sem_sub(client, usuario):
    token = _criar_token({"exp": datetime.now(timezone.utc) + timedelta(minutes=5)})

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401, resposta.text


def test_me_token_usuario_inexistente(client):
    token = _criar_token(
        {
            "sub": "999999",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }
    )

    resposta = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401, resposta.text


def test_me_usuario_desativado(client, usuario, headers):
    cancelamento = client.patch(f"/usuarios/{usuario['id']}/cancelar", headers=headers)
    assert cancelamento.status_code == 200, cancelamento.text

    resposta = client.get("/auth/me", headers=headers)

    assert resposta.status_code == 401, resposta.text


def test_me_usuario_removido(client, usuario, headers):
    remocao = client.delete(f"/usuarios/{usuario['id']}", headers=headers)
    assert remocao.status_code == 204, remocao.text

    resposta = client.get("/auth/me", headers=headers)

    assert resposta.status_code == 401, resposta.text
