from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    apellido: str
    usuario: str
    rol: str
    dni: str | None = None
