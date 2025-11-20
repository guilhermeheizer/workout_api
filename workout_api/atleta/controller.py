from uuid import UUID
from fastapi import APIRouter, Depends, Body, status
from fastapi_pagination import Page, paginate
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.atleta.atleta_crud import (
    criar_atleta,
    listar_atletas,
    buscar_atleta_por_id,
    atualizar_atleta,
    deletar_atleta
)

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency = Depends(),
    atleta_in: AtletaIn = Body(...)
):
    return await criar_atleta(db_session, atleta_in)


@router.get(
    '/', 
    summary='Consultar todos os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=Page[dict],
)
async def query(
    db_session: DatabaseDependency = Depends(),
    nome: str | None = None,
    cpf: str | None = None
):
    atletas = await listar_atletas(db_session, nome, cpf)
    return paginate(atletas)


@router.get(
    '/{id}', 
    summary='Consulta um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(
    id: UUID,
    db_session: DatabaseDependency = Depends()
):
    return await buscar_atleta_por_id(db_session, id)


@router.patch(
    '/{id}', 
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(
    id: UUID,
    db_session: DatabaseDependency = Depends(),
    atleta_update: AtletaUpdate = Body(...)
):
    return await atualizar_atleta(db_session, id, atleta_update)


@router.delete(
    '/{id}', 
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(
    id: UUID,
    db_session: DatabaseDependency = Depends()
):
    return await deletar_atleta(db_session, id)