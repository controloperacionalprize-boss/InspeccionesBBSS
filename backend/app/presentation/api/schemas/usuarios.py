from pydantic import BaseModel, Field

from app.presentation.api.schemas.auth import UsuarioResponse


class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=70)
    apellido: str = Field(..., min_length=1, max_length=70)
    usuario: str = Field(..., min_length=1, max_length=120)
    contrasena: str = Field(..., min_length=8, max_length=72)
    rol: str = Field(..., min_length=1, max_length=40)
    dni: str | None = Field(None, max_length=20)


class UsuarioUpdate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=70)
    apellido: str = Field(..., min_length=1, max_length=70)
    rol: str = Field(..., min_length=1, max_length=40)
    dni: str | None = Field(None, max_length=20)
    contrasena: str | None = Field(None, min_length=8, max_length=72)


class UsuarioRead(UsuarioResponse):
    dni: str | None = None
