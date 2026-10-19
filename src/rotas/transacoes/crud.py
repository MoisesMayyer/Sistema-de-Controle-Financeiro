from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dados.dependencies import get_db, verificar_token
from dados.models import Categoria, Transacao, Usuario
from dados.schemas import TransacaoCreate, TransacaoUpdate, TransacaoResponse

router_transacao = APIRouter(prefix="/transacoes", tags=["Transações"])


@router_transacao.get("/", response_model=list[TransacaoResponse])
def listar_transacoes(db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):

    transacoes = db.query(Transacao).filter(Transacao.usuario_id == usuario.id).all()

    return transacoes


@router_transacao.get("/{id}", response_model=TransacaoResponse)
def buscar_transacao(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):

    transacao = (
        db.query(Transacao)
        .filter(Transacao.id == id, Transacao.usuario_id == usuario.id)
        .first()
    )

    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    return transacao


@router_transacao.post("/", response_model=TransacaoResponse, status_code=201)
def adicionar_transacao(
    dados: TransacaoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    categoria_id = dados.categoria_id

    if categoria_id is not None:
        categoria = (
            db.query(Categoria)
            .filter(Categoria.id == categoria_id, Categoria.usuario_id == usuario.id)
            .first()
        )
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoria não encontrada")

    transacao = Transacao(
        descricao=dados.descricao,
        valor=dados.valor,
        tipo=dados.tipo,
        data=dados.data,
        categoria_id=categoria_id,
        usuario_id=usuario.id,
    )
    db.add(transacao)
    db.commit()
    db.refresh(transacao)
    return transacao


@router_transacao.put("/{id}", response_model=TransacaoResponse)
def editar_transacao(
    id: int,
    dados: TransacaoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    transacao = (
        db.query(Transacao)
        .filter(Transacao.id == id, Transacao.usuario_id == usuario.id)
        .first()
    )

    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    if dados.categoria_id is not None:
        categoria = (
            db.query(Categoria)
            .filter(Categoria.id == dados.categoria_id, Categoria.usuario_id == usuario.id)
            .first()
        )
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoria não encontrada")

    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transacao, field, value)

    db.commit()
    db.refresh(transacao)
    return transacao


@router_transacao.delete("/{id}")
def remover_transacao(id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)):

    transacao = (
        db.query(Transacao)
        .filter(Transacao.id == id, Transacao.usuario_id == usuario.id)
        .first()
    )

    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    db.delete(transacao)
    db.commit()
    return {"message": "Transação removida com sucesso"}
