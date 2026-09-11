from pydantic import BaseModel

from app.presentation.api.schemas.catalogos import (
    AreaRead,
    CategoriaRead,
    DivisionRead,
    EmpresaRead,
    FundoRead,
    SubcategoriaRead,
)


class CatalogosRead(BaseModel):
    empresas: list[EmpresaRead]
    fundos: list[FundoRead]
    divisiones: list[DivisionRead]
    areas: list[AreaRead]
    categorias: list[CategoriaRead]
    subcategorias: list[SubcategoriaRead]


class InspeccionesPorTipo(BaseModel):
    campo: int
    packing: int
    sin_tipo: int


class ResumenRead(BaseModel):
    inspecciones: int
    inspecciones_por_tipo: InspeccionesPorTipo
    inspecciones_sin_accion: int
    consultas_por_responder: int
    entregas: int
    unidades_entregadas: int
