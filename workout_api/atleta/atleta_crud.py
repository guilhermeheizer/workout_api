from datetime import datetime
from uuid import uuid4, UUID
from fastapi import HTTPException, status
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from workout_api.contrib.dependencies import DatabaseDependency


async def criar_atleta(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn
) -> AtletaOut:
    # Verifica se a categoria existe
    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=atleta_in.categoria.nome))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'A categoria {atleta_in.categoria.nome} não foi encontrada.'
        )

    # Verifica se o centro de treinamento existe
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'O centro de treinamento {atleta_in.centro_treinamento.nome} não foi encontrado.'
        )
    
    try:
        # Cria o AtletaOut e sua modelagem SQL
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.now(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        
        # Relaciona o atleta com a categoria e o centro de treinamento
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        
        db_session.add(atleta_model)
        await db_session.commit()

        return atleta_out

    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f"Já existe um atleta cadastrado com o CPF: {atleta_in.cpf}"
        )
    except Exception:
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao inserir os dados no banco"
        )


async def listar_atletas(
    db_session: DatabaseDependency,
    nome: str | None = None,
    cpf: str | None = None
) -> list[dict]:
    query = select(AtletaModel).join(CategoriaModel).join(CentroTreinamentoModel)

    # Adiciona filtros opcionais
    if nome:
        query = query.filter(AtletaModel.nome.ilike(f"%{nome}%"))
    if cpf:
        query = query.filter(AtletaModel.cpf == cpf)

    atletas = (await db_session.execute(query)).scalars().all()

    # Personaliza a resposta
    return [
        {
            "nome": atleta.nome,
            "centro_treinamento": atleta.centro_treinamento.nome,
            "categoria": atleta.categoria.nome
        }
        for atleta in atletas
    ]


async def buscar_atleta_por_id(db_session: DatabaseDependency, id: UUID) -> AtletaOut:
    atleta_model = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    return AtletaOut.model_validate(atleta_model)


async def atualizar_atleta(
    db_session: DatabaseDependency, 
    id: UUID, 
    atleta_update: AtletaUpdate
) -> AtletaOut:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )

    atleta_data = atleta_update.model_dump(exclude_unset=True)
    for key, value in atleta_data.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return AtletaOut.model_validate(atleta)


async def deletar_atleta(db_session: DatabaseDependency, id: UUID) -> None:
    atleta = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()