from sqlite3 import IntegrityError
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.categorias.models import CategoriaModel
from fastapi_pagination import Page, Params, paginate  

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/', 
    summary='Criar uma nova Categoria',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, 
    categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())
    
    # Verifica se a categoria existe
    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_in.nome))
    ).scalars().first()
    
    if categoria:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f'A categoria {categoria_in.nome} não foi encontrada.'
        )

    try:
        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe uma categoria cadastrada com o nome: {categoria_in.nome}"
        )

    return categoria_out
    
    
@router.get(
    '/', 
    summary='Consultar todas as Categorias',
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],  # Atualizamos o response_model para lidar com paginação
)
async def query(db_session: DatabaseDependency) -> Page[CategoriaOut]:
    # Recupere todas as categorias do banco de dados
    categoria_models = (await db_session.execute(select(CategoriaModel))).scalars().all()

    # Converta o modelo SQLAlchemy para CategoriaOut
    categorias = [CategoriaOut.model_validate(c) for c in categoria_models]
    
    # Use paginate para retornar os dados no formato paginado
    return paginate(categorias)


@router.get(
    '/{id}', 
    summary='Consulta uma Categoria pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria_model = (await db_session.execute(select(CategoriaModel).filter_by(id=id))).scalars().first()

    if not categoria_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada no id: {id}'
        )
    
    categoria_out = CategoriaOut.model_validate(categoria_model)
    return categoria_out