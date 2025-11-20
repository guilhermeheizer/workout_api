from uuid import UUID, uuid4
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from workout_api.categorias.models import CategoriaModel
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select


async def criar_categoria(
    db_session: DatabaseDependency, 
    categoria_in: CategoriaIn
) -> CategoriaOut:
    # Verifica se a categoria já existe pelo nome
    existe_categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_in.nome))
    ).scalars().first()
    
    if existe_categoria:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f"Já existe uma categoria cadastrada com o nome: {categoria_in.nome}"
        )

    # Cria os objetos de saída e modelo
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())
    
    try:
        # Adiciona ao banco de dados
        db_session.add(categoria_model)
        await db_session.commit()
        return categoria_out
    except IntegrityError:
        # Rollback no caso de erro de integridade
        await db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao tentar salvar a categoria no banco de dados."
        )


async def listar_categorias(
    db_session: DatabaseDependency
) -> list[CategoriaOut]:
    # Recupera todas as categorias do banco de dados
    categoria_models = (await db_session.execute(select(CategoriaModel))).scalars().all()

    # Converte os modelos para o esquema de saída
    return [CategoriaOut.model_validate(c) for c in categoria_models]


async def buscar_categoria_por_id(
    db_session: DatabaseDependency, 
    id: UUID
) -> CategoriaOut:
    # Busca uma categoria pelo ID
    categoria_model = (await db_session.execute(
        select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Categoria não encontrada no id: {id}"
        )

    # Converte o modelo para o esquema de saída
    return CategoriaOut.model_validate(categoria_model)