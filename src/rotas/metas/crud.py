from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from dados.dependencies import get_db
from dados.models import Meta
from dados.schemas import MetaCreate, MetaUpdate, MetaResponse

router_meta = APIRouter(prefix="/metas", tags=["Metas"])


def calcular_porcentagem_meta(valor_atual: float, valor_final: float) -> float:
    if valor_final == 0:
        return 0.0
    porcentagem = (valor_atual / valor_final) * 100
    return round(min(porcentagem, 100), 2)


def meta_to_response(meta: Meta) -> MetaResponse:
    return MetaResponse(
        id=meta.id,
        nome=meta.nome,
        valor_inicial=meta.valor_inicial,
        valor_final=meta.valor_final,
        data_inicio=meta.data_inicio,
        data_fim=meta.data_fim,
        porcentagem=calcular_porcentagem_meta(meta.valor_inicial, meta.valor_final),
    )


@router_meta.get("/", response_model=list[MetaResponse])
def listar_metas(db: Session = Depends(get_db)):
    metas = db.query(Meta).all()
    return [meta_to_response(m) for m in metas]


@router_meta.get("/{id}", response_model=MetaResponse)
def buscar_meta(id: int, db: Session = Depends(get_db)):
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return meta_to_response(meta)


@router_meta.post("/", response_model=MetaResponse, status_code=201)
def criar_meta(dados: MetaCreate, db: Session = Depends(get_db)):
    meta = Meta(
        nome=dados.nome,
        valor_inicial=dados.valor_inicial,
        valor_final=dados.valor_final,
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim,
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)


@router_meta.put("/{id}", response_model=MetaResponse)
def editar_meta(id: int, dados: MetaUpdate, db: Session = Depends(get_db)):
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meta, field, value)

    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)


@router_meta.delete("/{id}")
def remover_meta(id: int, db: Session = Depends(get_db)):
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db.delete(meta)
    db.commit()
    return {"message": "Meta removida com sucesso"}


@router_meta.post("/{id}/adicionar-valor", response_model=MetaResponse)
def adicionar_valor_meta(id: int, valor: float = Body(..., embed=True), db: Session = Depends(get_db)):
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    novo_valor = meta.valor_inicial + valor
    if novo_valor > meta.valor_final:
        raise HTTPException(status_code=400, detail="Valor excede o valor final da meta")

    meta.valor_inicial = novo_valor
    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)