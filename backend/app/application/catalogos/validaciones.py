"""Coherencia de FKs compartida por Consultas e Indumentaria (fundo de esa
empresa, área de esa división). Inspecciones tiene su propia validación en
app.application.inspecciones.validaciones porque además valida categoría/
subcategoría.
"""

from sqlalchemy.orm import Session

from app.infrastructure.database.models import Area, Division, Empresa, Fundo


class ReferenciaCatalogoInvalidaError(Exception):
    """Se lanza cuando alguna referencia de catálogo no existe o es incoherente."""


def validar_empresa_fundo_division_area(session: Session, datos) -> None:
    empresa = session.get(Empresa, datos.ID_EMPRESA)
    if empresa is None:
        raise ReferenciaCatalogoInvalidaError(f"La empresa {datos.ID_EMPRESA} no existe")

    fundo = session.get(Fundo, datos.ID_FUNDO)
    if fundo is None:
        raise ReferenciaCatalogoInvalidaError(f"El fundo {datos.ID_FUNDO} no existe")
    if fundo.ID_EMPRESA != datos.ID_EMPRESA:
        raise ReferenciaCatalogoInvalidaError("El fundo no pertenece a la empresa indicada")

    division = session.get(Division, datos.ID_DIVISION)
    if division is None:
        raise ReferenciaCatalogoInvalidaError(f"La división {datos.ID_DIVISION} no existe")

    area = session.get(Area, datos.ID_AREA)
    if area is None:
        raise ReferenciaCatalogoInvalidaError(f"El área {datos.ID_AREA} no existe")
    if area.ID_DIVISION != datos.ID_DIVISION:
        raise ReferenciaCatalogoInvalidaError("El área no pertenece a la división indicada")
