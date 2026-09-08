"""Coherencia de FKs de una inspección (fundo de esa empresa, área de esa división, etc.)."""

from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    Area,
    Categoria,
    Division,
    Empresa,
    Fundo,
    Subcategoria,
)


class InspeccionInvalidaError(Exception):
    """Se lanza cuando alguna referencia de catálogo no existe o es incoherente."""


def validar_referencias_inspeccion(session: Session, datos) -> None:
    """Verifica que todas las FKs existan y sean coherentes entre sí."""

    empresa = session.get(Empresa, datos.ID_EMPRESA)
    if empresa is None:
        raise InspeccionInvalidaError(f"La empresa {datos.ID_EMPRESA} no existe")

    fundo = session.get(Fundo, datos.ID_FUNDO)
    if fundo is None:
        raise InspeccionInvalidaError(f"El fundo {datos.ID_FUNDO} no existe")
    if fundo.ID_EMPRESA != datos.ID_EMPRESA:
        raise InspeccionInvalidaError("El fundo no pertenece a la empresa indicada")

    division = session.get(Division, datos.ID_DIVISION)
    if division is None:
        raise InspeccionInvalidaError(f"La división {datos.ID_DIVISION} no existe")

    area = session.get(Area, datos.ID_AREA)
    if area is None:
        raise InspeccionInvalidaError(f"El área {datos.ID_AREA} no existe")
    if area.ID_DIVISION != datos.ID_DIVISION:
        raise InspeccionInvalidaError("El área no pertenece a la división indicada")

    categoria = session.get(Categoria, datos.ID_CATEGORIA)
    if categoria is None:
        raise InspeccionInvalidaError(f"La categoría {datos.ID_CATEGORIA} no existe")

    subcategoria = session.get(Subcategoria, datos.ID_SUBCATEGORIA)
    if subcategoria is None:
        raise InspeccionInvalidaError(f"La subcategoría {datos.ID_SUBCATEGORIA} no existe")
    if subcategoria.ID_CATEGORIA != datos.ID_CATEGORIA:
        raise InspeccionInvalidaError("La subcategoría no pertenece a la categoría indicada")
