from uuid import UUID
from fastapi import APIRouter, Body, Depends, status
from fastapi_pagination import Page, paginate
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.contrib.dependencies import DatabaseDependency

from workout_api.centro_treinamento.centro_treinamento_crud import (
    criar_centro_treinamento,
    listar_centros_treinamento,
    buscar_centro_treinamento_por_id,
)

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo Centro de treinamento',
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency = Depends(), 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    return await criar_centro_treinamento(db_session, centro_treinamento_in)


@router.get(
    '/', 
    summary='Consultar todos os centros de treinamento',
    status_code=status.HTTP_200_OK,
    response_model=Page[CentroTreinamentoOut],
)
async def query(
    db_session: DatabaseDependency = Depends(),
) -> Page[CentroTreinamentoOut]:
    centros_treinamento_out = await listar_centros_treinamento(db_session)
    return paginate(centros_treinamento_out)


@router.get(
    '/{id}', 
    summary='Consulta um centro de treinamento pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get(
    id: UUID, 
    db_session: DatabaseDependency = Depends(),
) -> CentroTreinamentoOut:
    return await buscar_centro_treinamento_por_id(db_session, id)