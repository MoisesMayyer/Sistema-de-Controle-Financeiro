from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dados.dependencies import get_db
from dados.models import Categoria, TipoTransacao
from dados.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router_categoria = APIRouter(prefix="/categorias", tags=["Categorias"])


def calcular_porcentagem_limite(total_despesas: float, valor_limite: float) -> float:
    if valor_limite == 0:
        return 0.0
    return round(min((total_despesas / valor_limite) * 100, 100), 2)


def categoria_to_response(categoria: Categoria) -> CategoriaResponse:
    total_despesas = sum(t.valor for t in categoria.transacoes if t.tipo == TipoTransacao.DESPESA)
    total_receitas = sum(t.valor for t in categoria.transacoes if t.tipo == TipoTransacao.RECEITA)

    return CategoriaResponse(
        id=categoria.id,
        nome=categoria.nome,
        valor_inicial=categoria.valor_inicial,
        valor_limite=categoria.valor_limite,
        total_despesas=total_despesas,
        total_receitas=total_receitas,
        saldo=categoria.valor_inicial + total_receitas - total_despesas,
        porcentagem_limite=calcular_porcentagem_limite(total_despesas, categoria.valor_limite),
    )


@router_categoria.get("/", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return [categoria_to_response(c) for c in categorias]


@router_categoria.get("/{id}", response_model=CategoriaResponse)
def buscar_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria_to_response(categoria)


@router_categoria.post("/", response_model=CategoriaResponse, status_code=201)
def criar_categoria(dados: CategoriaCreate, db: Session = Depends(get_db)):
    existing = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
    if existing:
        raise HTTPException(status_code=400, detail="Categoria com este nome já existe")

    categoria = Categoria(
        nome=dados.nome,
        valor_inicial=dados.valor_inicial,
        valor_limite=dados.valor_limite,
    )
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria_to_response(categoria)


@router_categoria.put("/{id}", response_model=CategoriaResponse)
def editar_categoria(id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if dados.nome and dados.nome != categoria.nome:
        existing = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
        if existing:
            raise HTTPException(status_code=400, detail="Categoria com este nome já existe")

    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(categoria, field, value)

    db.commit()
    db.refresh(categoria)
    return categoria_to_response(categoria)


@router_categoria.delete("/{id}")
def remover_categoria(id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if categoria.transacoes:
        raise HTTPException(
            status_code=400,
            detail="Não é possível remover categoria com transações associadas"
        )

    db.delete(categoria)
    db.commit()
    return {"message": "Categoria removida com sucesso"}