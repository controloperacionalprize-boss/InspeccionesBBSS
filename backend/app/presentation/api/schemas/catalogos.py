from pydantic import BaseModel, Field, field_validator


class NombreMayusculas(BaseModel):
    """Los maestros se guardan en mayúsculas para evitar duplicados por mayúsculas/minúsculas."""

    @field_validator("NOMBRE", mode="before", check_fields=False)
    @classmethod
    def nombre_en_mayusculas(cls, valor: object) -> object:
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor


class EmpresaCreate(NombreMayusculas):
    NOMBRE: str = Field(..., min_length=1, max_length=30)


class EmpresaRead(EmpresaCreate):
    ID: int

    model_config = {"from_attributes": True}


class DivisionCreate(NombreMayusculas):
    NOMBRE: str = Field(..., min_length=1, max_length=100)


class DivisionRead(DivisionCreate):
    ID: int

    model_config = {"from_attributes": True}


class FundoBase(NombreMayusculas):
    NOMBRE: str = Field(..., min_length=1, max_length=50)
    ID_EMPRESA: int


class FundoCreate(FundoBase):
    pass


class FundoRead(FundoBase):
    ID: int

    model_config = {"from_attributes": True}


class AreaBase(NombreMayusculas):
    NOMBRE: str = Field(..., min_length=1, max_length=100)
    ID_DIVISION: int


class AreaCreate(AreaBase):
    pass


class AreaRead(AreaBase):
    ID: int

    model_config = {"from_attributes": True}


class CategoriaCreate(NombreMayusculas):
    NOMBRE: str = Field(..., min_length=1, max_length=150)


class CategoriaRead(CategoriaCreate):
    ID: int

    model_config = {"from_attributes": True}


class RolRead(BaseModel):
    ID: int
    NOMBRE: str

    model_config = {"from_attributes": True}


class SubcategoriaBase(NombreMayusculas):
    NOMBRE: str = Field(..., min_length=1, max_length=150)
    ID_CATEGORIA: int


class SubcategoriaCreate(SubcategoriaBase):
    pass


class SubcategoriaRead(SubcategoriaBase):
    ID: int

    model_config = {"from_attributes": True}
