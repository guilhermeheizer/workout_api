from sqlite3 import IntegrityError
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from fastapi_pagination import Page, Params, paginate 

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo Centro de treinamento',
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    # Criar objetos de entrada e modelo
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
    
    # Verifica se o centro de treinamento existe
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_in.nome))
    ).scalars().first()
    
    if centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f'O centro de treinamento {centro_treinamento_in.nome} já existe.'
        )
    
    try:
        # Adicionar ao banco e tentar salvar
        db_session.add(centro_treinamento_model)
        await db_session.commit()

    except IntegrityError:
        # Realizar rollback em caso de erro de integridade (duplicado)
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um centro de treinamento cadastrado com o nome: {centro_treinamento_in.nome}"
        )

    return centro_treinamento_out
    
    
@router.get(
    '/', 
    summary='Consultar todos os centros de treinamento',
    status_code=status.HTTP_200_OK,
    response_model=Page[CentroTreinamentoOut],  # Atualizado para lidar com paginação
)
async def query(db_session: DatabaseDependency) -> Page[CentroTreinamentoOut]:
    centros_treinamento_models = (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    centros_treinamento_out = [
        CentroTreinamentoOut.model_validate(model) for model in centros_treinamento_models
    ]
    return paginate(centros_treinamento_out)  # Retorna dados paginados automaticamente


@router.get(
    '/{id}', 
    summary='Consulta um centro de treinamento pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento_model = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not centro_treinamento_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )
    
    return CentroTreinamentoOut.model_validate(centro_treinamento_model)