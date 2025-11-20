from uuid import UUID, uuid4
from fastapi import HTTPException, status
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel

from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError


async def criar_centro_treinamento(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn
) -> CentroTreinamentoOut:
    # Verifica se o centro de treinamento já existe pelo nome
    existe_centro = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_in.nome))
    ).scalars().first()
    
    if existe_centro:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f'O centro de treinamento {centro_treinamento_in.nome} já existe.'
        )

    # Cria os objetos de saída e modelo
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
    
    try:
        # Adiciona ao banco de dados
        db_session.add(centro_treinamento_model)
        await db_session.commit()
        return centro_treinamento_out
    except IntegrityError:
        # Rollback no caso de erro de integridade
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um centro de treinamento cadastrado com o nome: {centro_treinamento_in.nome}"
        )


async def listar_centros_treinamento(
    db_session: DatabaseDependency
) -> list[CentroTreinamentoOut]:
    # Recupera todos os centros de treinamento
    centros_treinamento_models = (
        await db_session.execute(select(CentroTreinamentoModel))
    ).scalars().all()

    # Converte os dados para a saída desejada
    return [
        CentroTreinamentoOut.model_validate(model) for model in centros_treinamento_models
    ]


async def buscar_centro_treinamento_por_id(
    db_session: DatabaseDependency, 
    id: UUID
) -> CentroTreinamentoOut:
    # Busca o centro de treinamento pelo ID
    centro_treinamento_model = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )

    # Converte o modelo SQLAlchemy para o esquema de saída
    return CentroTreinamentoOut.model_validate(centro_treinamento_model)