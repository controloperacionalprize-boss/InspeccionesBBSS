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


def _preparar(session):
    rol = Rol(NOMBRE=ROL_INSPECTOR)
    session.add(rol)
    session.flush()
    usuario = Usuario(NOMBRE="I", APELLIDO="P", USUARIO="insp", PASSWORD_HASH=hash_password("x" * 10), ID_ROL=rol.ID)
    empresa, division, categoria = Empresa(NOMBRE="E"), Division(NOMBRE="D"), Categoria(NOMBRE="C")
    session.add_all([usuario, empresa, division, categoria])
    session.flush()
    fundo = Fundo(ID_EMPRESA=empresa.ID, NOMBRE="F")
    area = Area(ID_DIVISION=division.ID, NOMBRE="A")
    sub = Subcategoria(ID_CATEGORIA=categoria.ID, NOMBRE="S")
    session.add_all([fundo, area, sub])
    session.flush()
    ubicacion = dict(ID_EMPRESA=empresa.ID, ID_FUNDO=fundo.ID, ID_DIVISION=division.ID, ID_AREA=area.ID)

    def inspeccion(dia, tipo, accion=None, eliminado=False):
        return Inspeccion(
            **ubicacion, FECHA_OBSERVACION=date(2026, 9, dia), ID_CATEGORIA=categoria.ID,
            ID_SUBCATEGORIA=sub.ID, DESCRIPCION="d", TIPO_CONSULTA=tipo, ACCION_CORRECTIVA=accion,
            ELIMINADO=eliminado,
        )

    session.add_all([
        inspeccion(2, "Campo", "hecho"),
        inspeccion(3, "Campo"),
        inspeccion(4, "Packing", "  "),
        inspeccion(5, None),
        inspeccion(6, "Campo", eliminado=True),
        inspeccion(1, "Packing"),
        Consulta(**ubicacion, FECHA_CONSULTA=date(2026, 9, 2), DNI_TRABAJADOR="12345678", APELLIDOS_NOMBRES="X",
                 DESCRIPCION="d", AREA_RESPONSABLE="RR.HH."),
        Consulta(**ubicacion, FECHA_CONSULTA=date(2026, 9, 2), DNI_TRABAJADOR="12345678", APELLIDOS_NOMBRES="X",
                 DESCRIPCION="d", AREA_RESPONSABLE="RR.HH.", RESPUESTA_POSTERIOR="listo"),
        Indumentaria(**ubicacion, DNI_TRABAJADOR="12345678", APELLIDOS_NOMBRES="X", FECHA_ENTREGA=date(2026, 9, 3),
                     CANTIDAD=3, TIPO="Guantes", RESPONSABLE_REGISTRO="R"),
        Indumentaria(**ubicacion, DNI_TRABAJADOR="12345678", APELLIDOS_NOMBRES="X", FECHA_ENTREGA=date(2026, 8, 30),
                     CANTIDAD=5, TIPO="Botas", RESPONSABLE_REGISTRO="R"),
    ])
    session.commit()
    token = create_access_token(usuario.USUARIO, extra_claims={"uid": usuario.ID})
    return {"Authorization": f"Bearer {token}"}


def _cliente(db_session) -> TestClient:
    fabrica = sessionmaker(bind=db_session.bind)

    def _override():
        session = fabrica()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = _override
    return TestClient(app)


def test_listado_informa_total_filtrado_en_cabecera(db_session):
    headers = _preparar(db_session)
    client = _cliente(db_session)
    try:
        pagina = client.get("/api/inspecciones?limit=2&skip=0", headers=headers)
        assert pagina.status_code == 200
        assert len(pagina.json()) == 2
        assert pagina.headers["X-Total-Count"] == "5"  # la eliminada no cuenta

        filtrada = client.get("/api/inspecciones?tipo_consulta=Campo&limit=1", headers=headers)
        assert filtrada.headers["X-Total-Count"] == "2"
    finally:
        app.dependency_overrides.clear()


def test_resumen_cuenta_en_sql_sin_eliminados(db_session):
    headers = _preparar(db_session)
    client = _cliente(db_session)
    try:
        datos = client.get("/api/resumen?desde=2026-09-01", headers=headers).json()
        assert datos["inspecciones"] == 5
        assert datos["inspecciones_por_tipo"] == {"campo": 2, "packing": 2, "sin_tipo": 1}
        assert datos["inspecciones_sin_accion"] == 4  # None y solo espacios cuentan como vacía
        assert datos["consultas_por_responder"] == 1
        assert datos["entregas"] == 1
        assert datos["unidades_entregadas"] == 3
    finally:
        app.dependency_overrides.clear()


def test_catalogos_consolidados_en_una_respuesta(db_session):
    headers = _preparar(db_session)
    client = _cliente(db_session)
    try:
        datos = client.get("/api/catalogos", headers=headers).json()
        assert set(datos) == {"empresas", "fundos", "divisiones", "areas", "categorias", "subcategorias"}
        assert datos["fundos"][0]["ID_EMPRESA"] == datos["empresas"][0]["ID"]
    finally:
        app.dependency_overrides.clear()


def test_respuestas_grandes_se_comprimen(db_session):
    headers = _preparar(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.get("/api/inspecciones", headers={**headers, "Accept-Encoding": "gzip"})
        assert respuesta.headers.get("content-encoding") == "gzip"
    finally:
        app.dependency_overrides.clear()
