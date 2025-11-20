from uuid import UUID
from fastapi import APIRouter, Body, Depends, status
from fastapi_pagination import Page, paginate
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.contrib.dependencies import DatabaseDependency

from workout_api.categorias.categoria_crud import (
    criar_categoria,
    listar_categorias,
    buscar_categoria_por_id,
)

router = APIRouter()

@router.post(
    '/', 
    summary='Criar uma nova Categoria',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency = Depends(), 
    categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    return await criar_categoria(db_session, categoria_in)


@router.get(
    '/', 
    summary='Consultar todas as Categorias',
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],
)
async def query(
    db_session: DatabaseDependency = Depends(),
) -> Page[CategoriaOut]:
    categorias = await listar_categorias(db_session)
    return paginate(categorias)


@router.get(
    '/{id}', 
    summary='Consulta uma Categoria pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get(
    id: UUID, 
    db_session: DatabaseDependency = Depends(),
) -> CategoriaOut:
    return await buscar_categoria_por_id(db_session, id)