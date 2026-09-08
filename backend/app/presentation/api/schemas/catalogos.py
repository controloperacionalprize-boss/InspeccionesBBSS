"""Esquemas Pydantic para los catálogos base (con y sin FK simple)."""

from pydantic import BaseModel, Field


class CatalogoSimpleBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1)


class CatalogoSimpleCreate(CatalogoSimpleBase):
    pass


class CatalogoSimpleRead(CatalogoSimpleBase):
    ID: int

    model_config = {"from_attributes": True}


class FundoBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1)
    ID_EMPRESA: int


class FundoCreate(FundoBase):
    pass


class FundoRead(FundoBase):
    ID: int

    model_config = {"from_attributes": True}


class AreaBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1)
    ID_DIVISION: int


class AreaCreate(AreaBase):
    pass


class AreaRead(AreaBase):
    ID: int

    model_config = {"from_attributes": True}


class SubcategoriaBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1)
    ID_CATEGORIA: int


class SubcategoriaCreate(SubcategoriaBase):
    pass


class SubcategoriaRead(SubcategoriaBase):
    ID: int

    model_config = {"from_attributes": True}
