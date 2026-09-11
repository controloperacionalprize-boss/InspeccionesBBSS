from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.domain.roles import ROL_INSPECTOR
from app.infrastructure.database.models import Rol, Usuario
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt_handler import create_access_token
from app.infrastructure.security.password_hasher import hash_password
from app.presentation.api.app import app
from app.presentation.api.tiempo_real import avisar, hub


def _sembrar(session):
    rol = Rol(NOMBRE=ROL_INSPECTOR)
    session.add(rol)
    session.commit()
    usuario = Usuario(
        NOMBRE="Inspector",
        APELLIDO="Prueba",
        USUARIO="inspector_ws",
        PASSWORD_HASH=hash_password("clave-segura-123"),
        ID_ROL=rol.ID,
    )
    session.add(usuario)
    session.commit()
    return usuario


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


def test_websocket_rechaza_sin_token(db_session):
    client = _cliente(db_session)
    try:
        with client:
            with client.websocket_connect("/api/ws") as ws:
                ws.send_text("token-invalido")
                try:
                    ws.receive_text()
                    raise AssertionError("debía cerrar la conexión")
                except Exception:
                    pass
    finally:
        app.dependency_overrides.clear()


def test_websocket_cierre_antes_del_token_no_revienta(db_session):
    client = _cliente(db_session)
    try:
        with client:
            with client.websocket_connect("/api/ws"):
                pass
    finally:
        hub._conexiones.clear()
        app.dependency_overrides.clear()


def test_websocket_recibe_aviso_al_publicar(db_session):
    usuario = _sembrar(db_session)
    token = create_access_token(usuario.USUARIO, extra_claims={"uid": usuario.ID, "rol": ROL_INSPECTOR})
    client = _cliente(db_session)
    try:
        with client:
            with client.websocket_connect("/api/ws") as ws:
                ws.send_text(token)
                avisar("inspecciones")
                mensaje = ws.receive_json()
                assert mensaje == {"recurso": "inspecciones"}
    finally:
        hub._conexiones.clear()
        app.dependency_overrides.clear()
