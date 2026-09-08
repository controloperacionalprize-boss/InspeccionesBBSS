from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class InspeccionBase(BaseModel):
    ID_EMPRESA: int
    ID_FUNDO: int
    ID_DIVISION: int
    ID_AREA: int
    FECHA_OBSERVACION: date
    RANGO_HORA: datetime | None = None
    ID_CATEGORIA: int
    ID_SUBCATEGORIA: int
    DESCRIPCION: str = Field(..., min_length=1, max_length=8000)
    URL_FOTO: str | None = Field(None, max_length=2048)
    ACCION_CORRECTIVA: str | None = Field(None, max_length=8000)
    PLAZO_LEVANTAMIENTO: str | None = Field(None, max_length=500)
    TIPO_CONSULTA: Literal["Campo", "Packing"] | None = None


class InspeccionCreate(InspeccionBase):
    pass


class InspeccionRead(InspeccionBase):
    ID: int

    model_config = {"from_attributes": True}
