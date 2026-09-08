from pydantic import BaseModel, Field


class EmpresaCreate(BaseModel):
    NOMBRE: str = Field(..., min_length=1, max_length=30)


class EmpresaRead(EmpresaCreate):
    ID: int

    model_config = {"from_attributes": True}


class DivisionCreate(BaseModel):
    NOMBRE: str = Field(..., min_length=1, max_length=100)


class DivisionRead(DivisionCreate):
    ID: int

    model_config = {"from_attributes": True}


class FundoBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1, max_length=50)
    ID_EMPRESA: int


class FundoCreate(FundoBase):
    pass


class FundoRead(FundoBase):
    ID: int

    model_config = {"from_attributes": True}


class AreaBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1, max_length=100)
    ID_DIVISION: int


class AreaCreate(AreaBase):
    pass


class AreaRead(AreaBase):
    ID: int

    model_config = {"from_attributes": True}


class CategoriaCreate(BaseModel):
    NOMBRE: str = Field(..., min_length=1, max_length=150)


class CategoriaRead(CategoriaCreate):
    ID: int

    model_config = {"from_attributes": True}


class RolRead(BaseModel):
    ID: int
    NOMBRE: str

    model_config = {"from_attributes": True}


class SubcategoriaBase(BaseModel):
    NOMBRE: str = Field(..., min_length=1, max_length=150)
    ID_CATEGORIA: int


class SubcategoriaCreate(SubcategoriaBase):
    pass


class SubcategoriaRead(SubcategoriaBase):
    ID: int

    model_config = {"from_attributes": True}
