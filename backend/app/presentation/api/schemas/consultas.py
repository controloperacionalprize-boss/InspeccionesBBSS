from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ConsultaBase(BaseModel):
    ID_EMPRESA: int
    ID_FUNDO: int
    ID_DIVISION: int
    ID_AREA: int
    FECHA_CONSULTA: date
    DNI_TRABAJADOR: str = Field(..., pattern=r"^\d{8}$")
    APELLIDOS_NOMBRES: str = Field(..., min_length=1, max_length=150)
    DESCRIPCION: str = Field(..., min_length=1, max_length=8000)
    AREA_RESPONSABLE: str = Field(..., min_length=1, max_length=150)
    TIPO_CONSULTA: Literal["Campo", "Packing"] | None = None


class ConsultaCreate(ConsultaBase):
    """Alta desde el registro móvil: solo respuesta inmediata."""

    RESPUESTA_INMEDIATA: str | None = Field(None, max_length=8000)


class ConsultaUpdate(ConsultaBase):
    """Edición desde la web. RESPUESTA_INMEDIATA no se puede editar por aquí:
    es la respuesta capturada en campo y queda fija tras la creación."""

    RESPUESTA_POSTERIOR: str | None = Field(None, max_length=8000)


class ConsultaRead(ConsultaBase):
    ID: int
    RESPUESTA_INMEDIATA: str | None = None
    RESPUESTA_POSTERIOR: str | None = None
    ELIMINADO: bool
    FECHA_ELIMINACION: datetime | None = None

    model_config = {"from_attributes": True}
