from fastapi import FastAPI
from dados.database import Base, engine
from rotas.transacoes.crud import router_transacao
from rotas.categorias.crud import router_categoria
from rotas.metas.crud import router_meta

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Controle Financeiro API")

app.include_router(router_transacao)
app.include_router(router_categoria)
app.include_router(router_meta)


@app.get("/")
async def read_root():
    return {"message": "Controle Financeiro API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}