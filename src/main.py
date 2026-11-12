from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from rotas.transacoes.crud import router_transacao
from rotas.categorias.crud import router_categoria
from rotas.metas.crud import router_meta
from rotas.usuarios.crud import router_usuario
from rotas.auth.crud import router_auth
from rotas.relatorios.crud import router_relatorio

from dados.config import settings
app = FastAPI(title="Controle Financeiro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(router_transacao)
app.include_router(router_categoria)
app.include_router(router_meta)
app.include_router(router_usuario)
app.include_router(router_auth)
app.include_router(router_relatorio)


@app.get("/")
async def read_root():
    return {"message": "Controle Financeiro API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
