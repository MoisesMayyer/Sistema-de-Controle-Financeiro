from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dados.dependencies import get_db
from dados.models import Categoria
from dados.schemas import CategoriaCreate, CategoriaUpdate, CategoriaResponse

router_categoria = APIRouter(prefix="/categorias", tags=["Categorias"])


@router_categoria.get("/", response_model=list[CategoriaResponse])
def listar_categorias(db: Session = Depends(get_db)):
    """Lista todas as categorias."""
    categorias = db.query(Categoria).all()
    return categorias


@router_categoria.get("/{id}", response_model=CategoriaResponse)
def buscar_categoria(id: int, db: Session = Depends(get_db)):
    """Busca uma categoria pelo ID."""
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria


@router_categoria.post("/", response_model=CategoriaResponse, status_code=201)
def criar_categoria(dados: CategoriaCreate, db: Session = Depends(get_db)):
    """Cria uma nova categoria."""
    # Verifica se nome já existe
    existing = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
    if existing:
        raise HTTPException(status_code=400, detail="Categoria com este nome já existe")

    categoria = Categoria(
        nome=dados.nome,
        valor_inicial=float(dados.valor_inicial),
        valor_limite=float(dados.valor_limite),
    )
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router_categoria.put("/{id}", response_model=CategoriaResponse)
def editar_categoria(id: int, dados: CategoriaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma categoria existente."""
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # Verifica se nome já existe (se está sendo alterado)
    if dados.nome and dados.nome != categoria.nome:
        existing = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
        if existing:
            raise HTTPException(status_code=400, detail="Categoria com este nome já existe")

    # Atualiza apenas campos fornecidos
    update_data = dados.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ("valor_inicial", "valor_limite") and value is not None:
            value = float(value)
        setattr(categoria, field, value)

    db.commit()
    db.refresh(categoria)
    return categoria


@router_categoria.delete("/{id}")
def remover_categoria(id: int, db: Session = Depends(get_db)):
    """Remove uma categoria."""
    categoria = db.query(Categoria).filter(Categoria.id == id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # Verifica se há transações associadas
    if categoria.transacoes:
        raise HTTPException(
            status_code=400,
            detail="Não é possível remover categoria com transações associadas"
        )

    db.delete(categoria)
    db.commit()
    return {"message": "Categoria removida com sucesso"}