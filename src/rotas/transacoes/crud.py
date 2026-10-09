from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dados.dependencies import get_db
from dados.models import Transacao
from dados.schemas import TransacaoCreate, TransacaoUpdate, TransacaoResponse

router_transacao = APIRouter(prefix="/transacoes", tags=["Transações"])


@router_transacao.get("/", response_model=list[TransacaoResponse])
def listar_transacoes(db: Session = Depends(get_db)):
    """Lista todas as transações."""
    transacoes = db.query(Transacao).all()
    return transacoes


@router_transacao.get("/{id}", response_model=TransacaoResponse)
def buscar_transacao(id: int, db: Session = Depends(get_db)):
    """Busca uma transação pelo ID."""
    transacao = db.query(Transacao).filter(Transacao.id == id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transacao


@router_transacao.post("/", response_model=TransacaoResponse, status_code=201)
def adicionar_transacao(dados: TransacaoCreate, db: Session = Depends(get_db)):
    """Cria uma nova transação."""
    # Verifica se categoria existe (se fornecida)
    if dados.categoria_id:
        from dados.models import Categoria
        categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoria não encontrada")

    transacao = Transacao(
        descricao=dados.descricao,
        valor=float(dados.valor),
        tipo=dados.tipo,
        data=dados.data,
        categoria_id=dados.categoria_id,
    )
    db.add(transacao)
    db.commit()
    db.refresh(transacao)
    return transacao


@router_transacao.put("/{id}", response_model=TransacaoResponse)
def editar_transacao(id: int, dados: TransacaoUpdate, db: Session = Depends(get_db)):
    """Atualiza uma transação existente."""
    transacao = db.query(Transacao).filter(Transacao.id == id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # Verifica se categoria existe (se fornecida)
    if dados.categoria_id is not None:
        from dados.models import Categoria
        if dados.categoria_id > 0:
            categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
            if not categoria:
                raise HTTPException(status_code=400, detail="Categoria não encontrada")

    # Atualiza apenas campos fornecidos
    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "valor" and value is not None:
            value = float(value)
        setattr(transacao, field, value)

    db.commit()
    db.refresh(transacao)
    return transacao


@router_transacao.delete("/{id}")
def remover_transacao(id: int, db: Session = Depends(get_db)):
    """Remove uma transação."""
    transacao = db.query(Transacao).filter(Transacao.id == id).first()
    if not transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(transacao)
    db.commit()
    return {"message": "Transação removida com sucesso"}