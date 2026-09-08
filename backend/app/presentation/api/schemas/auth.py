from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    usuario: str = Field(..., min_length=1, max_length=120)
    contrasena: str = Field(..., min_length=1, max_length=72)


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    usuario: str
    rol: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
