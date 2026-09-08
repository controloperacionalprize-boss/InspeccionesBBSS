from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.domain.roles import ROL_ADMIN, ROL_INSPECTOR
from app.infrastructure.database.models import Rol, Usuario
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt_handler import create_access_token
from app.infrastructure.security.password_hasher import hash_password
from app.presentation.api.app import app


def _sembrar_usuarios(session):
    admin_rol = Rol(NOMBRE=ROL_ADMIN)
    inspector_rol = Rol(NOMBRE=ROL_INSPECTOR)
    session.add_all([admin_rol, inspector_rol])
    session.commit()
    admin = Usuario(
        NOMBRE="Admin",
        APELLIDO="Prueba",
        USUARIO="admin_http",
        PASSWORD_HASH=hash_password("clave-segura-123"),
        ID_ROL=admin_rol.ID,
    )
    inspector = Usuario(
        NOMBRE="Inspector",
        APELLIDO="Prueba",
        USUARIO="inspector_http",
        PASSWORD_HASH=hash_password("clave-segura-123"),
        ID_ROL=inspector_rol.ID,
    )
    session.add_all([admin, inspector])
    session.commit()
    return admin, inspector


def _headers(usuario: Usuario, rol_claim: str | None = None) -> dict[str, str]:
    token = create_access_token(
        usuario.USUARIO,
        extra_claims={"uid": usuario.ID, "rol": rol_claim or "ignorar"},
    )
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


def test_health_incluye_cabeceras_de_seguridad(db_session):
    client = _cliente(db_session)
    try:
        respuesta = client.get("/health")
        assert respuesta.status_code == 200
        assert respuesta.headers["X-Content-Type-Options"] == "nosniff"
        assert respuesta.headers["X-Frame-Options"] == "DENY"
        assert respuesta.headers["Referrer-Policy"] == "no-referrer"
    finally:
        app.dependency_overrides.clear()


def test_inspector_puede_listar_empresas_pero_no_crearlas(db_session):
    admin, inspector = _sembrar_usuarios(db_session)
    client = _cliente(db_session)
    try:
        listado = client.get("/api/empresas", headers=_headers(inspector))
        assert listado.status_code == 200

        alta = client.post(
            "/api/empresas",
            json={"NOMBRE": "ACME"},
            headers=_headers(inspector),
        )
        assert alta.status_code == 403

        alta_admin = client.post(
            "/api/empresas",
            json={"NOMBRE": "ACME"},
            headers=_headers(admin),
        )
        assert alta_admin.status_code == 201
    finally:
        app.dependency_overrides.clear()


def test_jwt_no_puede_escalar_rol_con_claim_admin(db_session):
    _admin, inspector = _sembrar_usuarios(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.post(
            "/api/empresas",
            json={"NOMBRE": "Hack"},
            headers=_headers(inspector, rol_claim=ROL_ADMIN),
        )
        assert respuesta.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_token_con_uid_ajeno_es_401(db_session):
    _admin, inspector = _sembrar_usuarios(db_session)
    client = _cliente(db_session)
    try:
        token = create_access_token(
            inspector.USUARIO,
            extra_claims={"uid": 99999, "rol": ROL_INSPECTOR},
        )
        respuesta = client.get(
            "/api/empresas",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert respuesta.status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_inspector_no_puede_borrar_inspecciones(db_session):
    admin, inspector = _sembrar_usuarios(db_session)
    client = _cliente(db_session)
    try:
        prohibido = client.delete("/api/inspecciones/1", headers=_headers(inspector))
        assert prohibido.status_code == 403

        ausente = client.delete("/api/inspecciones/1", headers=_headers(admin))
        assert ausente.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_empresa_nombre_excede_varchar(db_session):
    admin, _inspector = _sembrar_usuarios(db_session)
    client = _cliente(db_session)
    try:
        respuesta = client.post(
            "/api/empresas",
            json={"NOMBRE": "X" * 31},
            headers=_headers(admin),
        )
        assert respuesta.status_code == 422
    finally:
        app.dependency_overrides.clear()
