from typing import Annotated, Optional
from pydantic import Field, PositiveFloat
from workout_api.categorias.schemas import CategoriaIn
from workout_api.centro_treinamento.schemas import CentroTreinamentoAtleta

from workout_api.contrib.schemas import BaseSchema, OutMixin


class Atleta(BaseSchema):
     nome: Annotated[
        str, Field(max_length=50, description="Nome do atleta", json_schema_extra={"example": "Joao"})]
     cpf: Annotated[
        str, Field(max_length=11, description="CPF do atleta", json_schema_extra={"example": "12345678900"})]
     idade: Annotated[
        int, Field(description="Idade do atleta", json_schema_extra={"example": 25})]
     peso: Annotated[
        PositiveFloat, Field(description="Peso do atleta", json_schema_extra={"example": 75.5})]
     altura: Annotated[
        PositiveFloat, Field(description="Altura do atleta", json_schema_extra={"example": 1.70})]
     sexo: Annotated[
        str, Field(max_length=1, description="Sexo do atleta", json_schema_extra={"example": "M"})]
     categoria: Annotated[
        CategoriaIn, Field(description="Categoria do atleta")]
     centro_treinamento: Annotated[
        CentroTreinamentoAtleta, Field(description="Centro de treinamento do atleta")]

class AtletaIn(Atleta):
    pass


class AtletaOut(Atleta, OutMixin):
    pass

class AtletaUpdate(BaseSchema):
    nome: Annotated[
        Optional[str],
        Field(
            None,
            max_length=50,
            description="Nome do atleta",
            json_schema_extra={"example": "Joao"},
        ),
    ]
    idade: Annotated[
        Optional[int],
        Field(
            None,
            description="Idade do atleta",
            json_schema_extra={"example": 25},
        ),
    ]