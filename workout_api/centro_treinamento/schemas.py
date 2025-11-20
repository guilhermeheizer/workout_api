from typing import Annotated

from pydantic import Field, UUID4
from workout_api.contrib.schemas import BaseSchema


class CentroTreinamentoIn(BaseSchema):
    nome: Annotated[
        str, Field(max_length=20, description='Nome do centro de treinamento', json_schema_extra={"example": "Scale"})
        ]
    endereco: Annotated[
        str, Field(max_length=60, description='Endereço do centro de treinamento', json_schema_extra={"example": "Rua X, Q02"})
        ]
    proprietario: Annotated[
        str, Field(max_length=30, description='Proprietario do centro de treinamento', json_schema_extra={"example": "Guilherme Gama"})
        ]


class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[
        str, Field(max_length=20, description='Nome do centro de treinamento', json_schema_extra={"example": "Scale"})
        ]


class CentroTreinamentoOut(CentroTreinamentoIn):
    id: Annotated[
        UUID4, Field(description='Identificador do centro de treinamento')
        ]    