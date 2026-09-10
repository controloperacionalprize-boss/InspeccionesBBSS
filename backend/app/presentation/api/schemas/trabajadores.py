from pydantic import BaseModel


class TrabajadorRead(BaseModel):
    DNI: str
    APELLIDOS_NOMBRES: str
    EMPRESA: str | None = None
    CARGO: str | None = None
    VIGENTE: bool
