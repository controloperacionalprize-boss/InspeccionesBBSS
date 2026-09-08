from types import SimpleNamespace

import pytest

from app.application.inspecciones.validaciones import (
    InspeccionInvalidaError,
    validar_referencias_inspeccion,
)
from app.infrastructure.database.models import (
    Area,
    Categoria,
    Division,
    Empresa,
    Fundo,
    Subcategoria,
)


@pytest.fixture()
def catalogos(db_session):
    """Crea un árbol mínimo de catálogos coherentes entre sí (una Empresa con
    su Fundo, una División con su Área, una Categoría con su Subcategoría)."""
    empresa = Empresa(NOMBRE="Empresa Test")
    division = Division(NOMBRE="Division Test")
    categoria = Categoria(NOMBRE="Categoria Test")
    db_session.add_all([empresa, division, categoria])
    db_session.flush()

    fundo = Fundo(NOMBRE="Fundo Test", ID_EMPRESA=empresa.ID)
    area = Area(NOMBRE="Area Test", ID_DIVISION=division.ID)
    subcategoria = Subcategoria(NOMBRE="Subcategoria Test", ID_CATEGORIA=categoria.ID)
    db_session.add_all([fundo, area, subcategoria])
    db_session.commit()

    return SimpleNamespace(
        empresa=empresa,
        division=division,
        categoria=categoria,
        fundo=fundo,
        area=area,
        subcategoria=subcategoria,
    )


def _datos_validos(catalogos) -> SimpleNamespace:
    return SimpleNamespace(
        ID_EMPRESA=catalogos.empresa.ID,
        ID_FUNDO=catalogos.fundo.ID,
        ID_DIVISION=catalogos.division.ID,
        ID_AREA=catalogos.area.ID,
        ID_CATEGORIA=catalogos.categoria.ID,
        ID_SUBCATEGORIA=catalogos.subcategoria.ID,
    )


def test_referencias_coherentes_no_lanzan_error(db_session, catalogos):
    validar_referencias_inspeccion(db_session, _datos_validos(catalogos))


def test_empresa_inexistente_lanza_error(db_session, catalogos):
    datos = _datos_validos(catalogos)
    datos.ID_EMPRESA = 999999

    with pytest.raises(InspeccionInvalidaError):
        validar_referencias_inspeccion(db_session, datos)


def test_area_inexistente_lanza_error(db_session, catalogos):
    datos = _datos_validos(catalogos)
    datos.ID_AREA = 999999

    with pytest.raises(InspeccionInvalidaError):
        validar_referencias_inspeccion(db_session, datos)


def test_fundo_de_otra_empresa_lanza_error(db_session, catalogos):
    # El Fundo existe, pero pertenece a una Empresa distinta a la indicada:
    # esta es la regla de coherencia, no solo de existencia.
    otra_empresa = Empresa(NOMBRE="Otra Empresa")
    db_session.add(otra_empresa)
    db_session.commit()

    datos = _datos_validos(catalogos)
    datos.ID_EMPRESA = otra_empresa.ID

    with pytest.raises(InspeccionInvalidaError, match="no pertenece"):
        validar_referencias_inspeccion(db_session, datos)


def test_area_de_otra_division_lanza_error(db_session, catalogos):
    otra_division = Division(NOMBRE="Otra Division")
    db_session.add(otra_division)
    db_session.commit()

    datos = _datos_validos(catalogos)
    datos.ID_DIVISION = otra_division.ID

    with pytest.raises(InspeccionInvalidaError, match="no pertenece"):
        validar_referencias_inspeccion(db_session, datos)


def test_subcategoria_de_otra_categoria_lanza_error(db_session, catalogos):
    otra_categoria = Categoria(NOMBRE="Otra Categoria")
    db_session.add(otra_categoria)
    db_session.commit()

    datos = _datos_validos(catalogos)
    datos.ID_CATEGORIA = otra_categoria.ID

    with pytest.raises(InspeccionInvalidaError, match="no pertenece"):
        validar_referencias_inspeccion(db_session, datos)
