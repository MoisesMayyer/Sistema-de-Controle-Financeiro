from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from dados.dependencies import get_db, verificar_token
from dados.models import Transacao, TipoTransacao, Usuario
from dados.schemas import (
    RelatorioValorResponse,
    TransacaoListResponse,
    TransacaoResponse,
)

router_relatorio = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router_relatorio.get("/receitas", response_model=TransacaoListResponse)
def pegar_receitas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    busca: Optional[str] = Query(None),
):
    query = db.query(Transacao).filter(
        Transacao.usuario_id == usuario.id,
        Transacao.tipo == TipoTransacao.RECEITA,
    )

    if busca:
        query = query.filter(Transacao.descricao.ilike(f"%{busca}%"))

    total = query.count()

    transacoes = (
        query.order_by(Transacao.data.desc(), Transacao.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return TransacaoListResponse(
        items=[TransacaoResponse.model_validate(t) for t in transacoes],
        total=total,
        skip=skip,
        limit=limit,
    )


@router_relatorio.get("/despesas", response_model=TransacaoListResponse)
def pegar_despesas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    busca: Optional[str] = Query(None),
):
    query = db.query(Transacao).filter(
        Transacao.usuario_id == usuario.id,
        Transacao.tipo == TipoTransacao.DESPESA,
    )

    if busca:
        query = query.filter(Transacao.descricao.ilike(f"%{busca}%"))

    total = query.count()

    transacoes = (
        query.order_by(Transacao.data.desc(), Transacao.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return TransacaoListResponse(
        items=[TransacaoResponse.model_validate(t) for t in transacoes],
        total=total,
        skip=skip,
        limit=limit,
    )


@router_relatorio.get("/valor_receita", response_model=RelatorioValorResponse)
def pegar_valor_receitas(
    ano: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    # Intervalo do mês: do dia 1 até o dia 1 do mês seguinte (exclusivo).
    inicio = date(ano, mes, 1)
    fim = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)

    total = (
        db.query(func.coalesce(func.sum(Transacao.valor), 0.0))
        .filter(
            Transacao.usuario_id == usuario.id,
            Transacao.tipo == TipoTransacao.RECEITA,
            Transacao.data >= inicio,
            Transacao.data < fim,
        )
        .scalar()
    )

    return RelatorioValorResponse(valor_total=total)


@router_relatorio.get("/valor_despesas", response_model=RelatorioValorResponse)
def pegar_valor_despesas(
    ano: int = Query(..., ge=2000, le=2100),
    mes: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    inicio = date(ano, mes, 1)
    fim = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)

    total = (
        db.query(func.coalesce(func.sum(Transacao.valor), 0.0))
        .filter(
            Transacao.usuario_id == usuario.id,
            Transacao.tipo == TipoTransacao.DESPESA,
            Transacao.data >= inicio,
            Transacao.data < fim,
        )
        .scalar()
    )

    return RelatorioValorResponse(valor_total=total)
