from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from dados.dependencies import get_db, verificar_token
from dados.models import Meta, Usuario
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
        usuario_id=meta.usuario_id,
        nome=meta.nome,
        valor_inicial=meta.valor_inicial,
        valor_final=meta.valor_final,
        data_inicio=meta.data_inicio,
        data_fim=meta.data_fim,
        porcentagem=calcular_porcentagem_meta(meta.valor_inicial, meta.valor_final),
    )


@router_meta.get("/", response_model=list[MetaResponse])
def listar_metas(db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):
    metas = db.query(Meta).filter(Meta.usuario_id == usuario.id).all()
    return [meta_to_response(m) for m in metas]


@router_meta.get("/{id}", response_model=MetaResponse)
def buscar_meta(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):

    meta = db.query(Meta).filter(Meta.id == id, Meta.usuario_id == usuario.id).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    return meta_to_response(meta)


@router_meta.post("/", response_model=MetaResponse, status_code=201)
def criar_meta(
    dados: MetaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    meta = Meta(
        nome=dados.nome,
        valor_inicial=dados.valor_inicial,
        valor_final=dados.valor_final,
        data_inicio=dados.data_inicio,
        data_fim=dados.data_fim,
        usuario_id=usuario.id,
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)


@router_meta.put("/{id}", response_model=MetaResponse)
def editar_meta(
    id: int,
    dados: MetaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    meta = db.query(Meta).filter(Meta.id == id, Meta.usuario_id == usuario.id).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    valor_inicial = dados.valor_inicial if dados.valor_inicial is not None else meta.valor_inicial
    valor_final = dados.valor_final if dados.valor_final is not None else meta.valor_final

    if valor_final < valor_inicial:
        raise HTTPException(
            status_code=400,
            detail="valor_final não pode ser menor que valor_inicial",
        )

    data_inicio = dados.data_inicio if dados.data_inicio is not None else meta.data_inicio
    data_fim = dados.data_fim if dados.data_fim is not None else meta.data_fim

    if data_inicio and data_fim and data_fim <= data_inicio:
        raise HTTPException(
            status_code=400,
            detail="data_fim deve ser posterior a data_inicio",
        )

    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meta, field, value)

    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)


@router_meta.delete("/{id}")
def remover_meta(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):

    meta = db.query(Meta).filter(Meta.id == id, Meta.usuario_id == usuario.id).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    db.delete(meta)
    db.commit()
    return {"message": "Meta removida com sucesso"}


@router_meta.post("/{id}/adicionar-valor", response_model=MetaResponse)
def adicionar_valor_meta(
    id: int,
    valor: float = Body(..., gt=0, embed=True),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    meta = db.query(Meta).filter(Meta.id == id, Meta.usuario_id == usuario.id).first()

    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")

    novo_valor = meta.valor_inicial + valor
    if novo_valor > meta.valor_final:
        raise HTTPException(status_code=400, detail="Valor excede o valor final da meta")

    meta.valor_inicial = novo_valor
    db.commit()
    db.refresh(meta)
    return meta_to_response(meta)
