from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class IndumentariaBase(BaseModel):
    ID_EMPRESA: int
    ID_FUNDO: int
    ID_DIVISION: int
    ID_AREA: int
    DNI_TRABAJADOR: str = Field(..., pattern=r"^\d{8}$")
    APELLIDOS_NOMBRES: str = Field(..., min_length=1, max_length=150)
    FECHA_ENTREGA: date
    CANTIDAD: int = Field(..., gt=0)
    TIPO: str = Field(..., min_length=1, max_length=100)
    FIRMA: str = Field("", max_length=8000)
    RESPONSABLE_REGISTRO: str = Field(..., min_length=1, max_length=150)
    TIPO_CONSULTA: Literal["Campo", "Packing"] | None = None


class IndumentariaCreate(IndumentariaBase):
    pass


class IndumentariaRead(IndumentariaBase):
    ID: int
    ELIMINADO: bool
    FECHA_ELIMINACION: datetime | None = None

    model_config = {"from_attributes": True}
