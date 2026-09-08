"""Esquemas Pydantic para las inspecciones de Campo/Packing."""

from datetime import date, datetime

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
    DESCRIPCION: str = Field(..., min_length=1)
    URL_FOTO: str | None = None
    ACCION_CORRECTIVA: str | None = None
    PLAZO_LEVANTAMIENTO: str | None = None
    TIPO_CONSULTA: str | None = None


class InspeccionCreate(InspeccionBase):
    pass


class InspeccionRead(InspeccionBase):
    ID: int

    model_config = {"from_attributes": True}
