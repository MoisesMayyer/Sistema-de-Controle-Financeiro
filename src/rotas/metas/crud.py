from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from decimal import Decimal

from dados.dependencies import get_db
from dados.models import Meta
from dados.schemas import MetaCreate, MetaUpdate, MetaResponse

router_meta = APIRouter(prefix="/metas", tags=["Metas"])


def calcular_porcentagem_meta(valor_atual: float, valor_final: float) -> Decimal:
    """Calcula a porcentagem da meta."""
    if valor_final == 0:
        return Decimal("0")
    porcentagem = (valor_atual / valor_final) * 100
    return Decimal(str(min(porcentagem, 100))).quantize(Decimal("0.01"))


def meta_to_response(meta: Meta) -> MetaResponse:
    """Converte model Meta para schema MetaResponse."""
    return MetaResponse(
        id=meta.id,
        nome=meta.nome,
        valor_inicial=Decimal(str(meta.valor_inicial)),
        valor_final=Decimal(str(meta.valor_final)),
        data_inicio=meta.data_inicio,
        data_fim=meta.data_fim,
        porcentagem=calcular_porcentagem_meta(meta.valor_inicial, meta.valor_final),
    )


@router_meta.get("/", response_model=list[MetaResponse])
def listar_metas(db: Session = Depends(get_db)):
    """Lista todas as metas."""
    metas = db.query(Meta).all()
    return [meta_to_response(m) for m in metas]


@router_meta.get("/{id}", response_model=MetaResponse)
def buscar_meta(id: int, db: Session = Depends(get_db)):
    """Busca uma meta pelo ID."""
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return meta_to_response(meta)


@router_meta.post("/", response_model=MetaResponse, status_code=201)
def criar_meta(dados: MetaCreate, db: Session = Depends(get_db)):
    """Cria uma nova meta."""
    meta = Meta(
        nome=dados.nome,
        valor_inicial=float(dados.valor_inicial),
        valor_final=float(dados.valor_final),
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim,
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)


@router_meta.put("/{id}", response_model=MetaResponse)
def editar_meta(id: int, dados: MetaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma meta existente."""
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ("valor_inicial", "valor_final") and value is not None:
            value = float(value)
        setattr(meta, field, value)

    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)


@router_meta.delete("/{id}")
def remover_meta(id: int, db: Session = Depends(get_db)):
    """Remove uma meta."""
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db.delete(meta)
    db.commit()
    return {"message": "Meta removida com sucesso"}


@router_meta.post("/{id}/adicionar-valor", response_model=MetaResponse)
def adicionar_valor_meta(id: int, valor: Decimal = Body(..., embed=True), db: Session = Depends(get_db)):
    """Adiciona valor a uma meta."""
    meta = db.query(Meta).filter(Meta.id == id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    novo_valor = meta.valor_inicial + float(valor)
    if novo_valor > meta.valor_final:
        raise HTTPException(status_code=400, detail="Valor excede o valor final da meta")

    meta.valor_inicial = novo_valor
    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)