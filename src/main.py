from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from rotas.transacoes.crud import router_transacao
from rotas.categorias.crud import router_categoria
from rotas.metas.crud import router_meta
from rotas.usuarios.crud import router_usuario
from rotas.auth.crud import router_auth
from rotas.relatorios.crud import router_relatorio

from dados.limiter import LIMITE_GET, limiter
from dados.config import settings


app = FastAPI(title="Controle Financeiro API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


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
@limiter.limit(LIMITE_GET)
async def read_root(request: Request):
    return {"message": "Controle Financeiro API", "version": "1.0.0"}


@app.get("/health")
@limiter.limit(LIMITE_GET)
async def health_check(request: Request):
    return {"status": "healthy"}
