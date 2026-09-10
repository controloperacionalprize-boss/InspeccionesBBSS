from datetime import datetime

from pydantic import BaseModel


class FotoRead(BaseModel):
    ID: int
    URL: str
    ORDEN: int
    FECHA_SUBIDA: datetime

    model_config = {"from_attributes": True}
