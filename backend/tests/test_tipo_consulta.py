from app.application.catalogos.validaciones import (
    aplicar_tipo_consulta,
    tipo_consulta_segun_division,
)
from app.infrastructure.database.models import Division


def test_packing_en_mayusculas_es_packing():
    assert tipo_consulta_segun_division("PACKING") == "Packing"


def test_packing_con_texto_alrededor_es_packing():
    assert tipo_consulta_segun_division("PACKING BBSS") == "Packing"


def test_otra_division_es_campo():
    assert tipo_consulta_segun_division("CAMPO") == "Campo"
    assert tipo_consulta_segun_division("PRODUCCIÓN") == "Campo"
    assert tipo_consulta_segun_division(None) == "Campo"


def test_aplicar_tipo_consulta_usa_la_division(db_session):
    packing = Division(NOMBRE="PACKING")
    db_session.add(packing)
    db_session.commit()

    payload = aplicar_tipo_consulta(db_session, {"ID_DIVISION": packing.ID, "TIPO_CONSULTA": "Campo"})
    assert payload["TIPO_CONSULTA"] == "Packing"


def test_aplicar_tipo_consulta_campo_si_no_es_packing(db_session):
    campo = Division(NOMBRE="CAMPO")
    db_session.add(campo)
    db_session.commit()

    payload = aplicar_tipo_consulta(
        db_session,
        {"ID_DIVISION": campo.ID, "TIPO_CONSULTA": "Packing"},
    )
    assert payload["TIPO_CONSULTA"] == "Campo"
