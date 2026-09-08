import pytest
from sqlalchemy.orm import Session

from app.application.auth.login_usuario import login_usuario
from app.domain.exceptions import CredencialesInvalidasError
from app.domain.roles import ROL_ADMIN, ROL_INSPECTOR
from app.infrastructure.database.models import Rol, Usuario
from app.infrastructure.security.password_hasher import hash_password


def _sembrar_roles(session: Session) -> dict[str, Rol]:
    admin = Rol(NOMBRE=ROL_ADMIN)
    inspector = Rol(NOMBRE=ROL_INSPECTOR)
    session.add_all([admin, inspector])
    session.commit()
    return {ROL_ADMIN: admin, ROL_INSPECTOR: inspector}


def _crear_usuario(session, usuario="demo", contrasena="clave-segura-123", rol=ROL_INSPECTOR):
    roles = {r.NOMBRE: r for r in session.query(Rol).all()}
    if not roles:
        roles = _sembrar_roles(session)
    modelo = Usuario(
        NOMBRE="Nombre",
        APELLIDO="Apellido",
        USUARIO=usuario,
        PASSWORD_HASH=hash_password(contrasena),
        ID_ROL=roles[rol].ID,
    )
    session.add(modelo)
    session.commit()
    return modelo


def test_login_con_credenciales_correctas_devuelve_entidad_de_dominio(db_session):
    _crear_usuario(db_session, usuario="demo", contrasena="clave-segura-123")

    resultado = login_usuario(db_session, "demo", "clave-segura-123")

    assert resultado.usuario == "demo"
    assert resultado.nombre == "Nombre"
    assert resultado.apellido == "Apellido"
    assert resultado.rol == ROL_INSPECTOR


def test_login_admin_incluye_rol_admin(db_session):
    _crear_usuario(db_session, usuario="jefe", contrasena="clave-segura-123", rol=ROL_ADMIN)
    resultado = login_usuario(db_session, "jefe", "clave-segura-123")
    assert resultado.rol == ROL_ADMIN


def test_login_con_contrasena_incorrecta_lanza_credenciales_invalidas(db_session):
    _crear_usuario(db_session, usuario="demo", contrasena="clave-segura-123")

    with pytest.raises(CredencialesInvalidasError):
        login_usuario(db_session, "demo", "clave-equivocada")


def test_login_con_usuario_inexistente_lanza_credenciales_invalidas(db_session):
    with pytest.raises(CredencialesInvalidasError):
        login_usuario(db_session, "no_existe", "cualquier-clave")
