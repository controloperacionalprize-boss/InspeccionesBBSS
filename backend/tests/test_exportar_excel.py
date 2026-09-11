from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.domain.roles import ROL_INSPECTOR
from app.infrastructure.database.models import (
    Area,
    Categoria,
    Consulta,
    Division,
    Empresa,
    Fundo,
    Indumentaria,
    Inspeccion,
    Rol,
    Subcategoria,
    Usuario,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt_handler import create_access_token
from app.infrastructure.security.password_hasher import hash_password
from app.presentation.api.app import app

CONTENT_TYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _sembrar(session):
    rol = Rol(NOMBRE=ROL_INSPECTOR)
    session.add(rol)
    session.commit()
    usuario = Usuario(
        NOMBRE="Inspector",
        APELLIDO="Prueba",
        USUARIO="inspector_export",
        PASSWORD_HASH=hash_password("clave-segura-123"),
        ID_ROL=rol.ID,
    )
    session.add(usuario)

    empresa = Empresa(NOMBRE="ACME")
    session.add(empresa)
    session.commit()
    fundo = Fundo(ID_EMPRESA=empresa.ID, NOMBRE="Fundo 1")
    division = Division(NOMBRE="División 1")
    session.add_all([fundo, division])
    session.commit()
    area = Area(ID_DIVISION=division.ID, NOMBRE="Área 1")
    categoria = Categoria(NOMBRE="Categoría 1")
    session.add_all([area, categoria])
    session.commit()
    subcategoria = Subcategoria(ID_CATEGORIA=categoria.ID, NOMBRE="Subcategoría 1")
    session.add(subcategoria)
    session.commit()

    inspeccion = Inspeccion(
        ID_EMPRESA=empresa.ID,
        ID_FUNDO=fundo.ID,
        ID_DIVISION=division.ID,
        ID_AREA=area.ID,
        FECHA_OBSERVACION=date(2026, 1, 1),
        ID_CATEGORIA=categoria.ID,
        ID_SUBCATEGORIA=subcategoria.ID,
        DESCRIPCION="Hallazgo de prueba",
    )
    consulta = Consulta(
        ID_EMPRESA=empresa.ID,
        ID_FUNDO=fundo.ID,
        ID_DIVISION=division.ID,
        ID_AREA=area.ID,
        FECHA_CONSULTA=date(2026, 1, 1),
        DNI_TRABAJADOR="12345678",
        APELLIDOS_NOMBRES="Trabajador Prueba",
        DESCRIPCION="Consulta de prueba",
        AREA_RESPONSABLE="RRHH",
    )
    indumentaria = Indumentaria(
        ID_EMPRESA=empresa.ID,
        ID_FUNDO=fundo.ID,
        ID_DIVISION=division.ID,
        ID_AREA=area.ID,
        DNI_TRABAJADOR="12345678",
        APELLIDOS_NOMBRES="Trabajador Prueba",
        FECHA_ENTREGA=date(2026, 1, 1),
        CANTIDAD=2,
        TIPO="Guantes",
        FIRMA="",
        RESPONSABLE_REGISTRO="Inspector Prueba",
    )
    session.add_all([inspeccion, consulta, indumentaria])
    session.commit()
    return usuario


def _headers(usuario: Usuario) -> dict[str, str]:
    token = create_access_token(usuario.USUARIO, extra_claims={"uid": usuario.ID, "rol": ROL_INSPECTOR})
    return {"Authorization": f"Bearer {token}"}


def _cliente(db_session) -> TestClient:
    fabrica = sessionmaker(bind=db_session.bind)

    def _override_session():
        session = fabrica()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override_session
    return TestClient(app)


def test_exportar_inspecciones_devuelve_xlsx(db_session):
    usuario = _sembrar(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.get("/api/inspecciones/exportar", headers=_headers(usuario))
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"] == CONTENT_TYPE_XLSX
        assert "inspecciones_" in respuesta.headers["content-disposition"]
        assert len(respuesta.content) > 0
    finally:
        app.dependency_overrides.clear()


def test_exportar_consultas_devuelve_xlsx(db_session):
    usuario = _sembrar(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.get("/api/consultas/exportar", headers=_headers(usuario))
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"] == CONTENT_TYPE_XLSX
        assert len(respuesta.content) > 0
    finally:
        app.dependency_overrides.clear()


def test_exportar_indumentaria_devuelve_xlsx_con_firma_vacia(db_session):
    usuario = _sembrar(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.get("/api/indumentaria/exportar", headers=_headers(usuario))
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"] == CONTENT_TYPE_XLSX
        assert len(respuesta.content) > 0
    finally:
        app.dependency_overrides.clear()


def test_exportar_respeta_filtro_de_empresa(db_session):
    usuario = _sembrar(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.get(
            "/api/inspecciones/exportar",
            params={"id_empresa": 9999},
            headers=_headers(usuario),
        )
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"] == CONTENT_TYPE_XLSX
    finally:
        app.dependency_overrides.clear()
