import pytest

from app.application.usuarios.gestionar import crear_usuario, obtener_usuario
from app.domain.exceptions import DatosInvalidosError, RolInvalidoError, UsuarioDuplicadoError
from app.domain.roles import ROL_ADMIN, ROL_INSPECTOR
from app.infrastructure.database.models import Rol


def _sembrar_roles(session):
    session.add_all([Rol(NOMBRE=ROL_ADMIN), Rol(NOMBRE=ROL_INSPECTOR)])
    session.commit()


def test_crear_usuario_inspector(db_session):
    _sembrar_roles(db_session)
    creado = crear_usuario(
        db_session,
        nombre="Ana",
        apellido="Perez",
        usuario="ana",
        contrasena="clave-segura-123",
        rol=ROL_INSPECTOR,
    )
    assert creado.usuario == "ana"
    assert creado.rol == ROL_INSPECTOR
    assert obtener_usuario(db_session, creado.id).nombre == "Ana"


def test_crear_usuario_duplicado(db_session):
    _sembrar_roles(db_session)
    crear_usuario(
        db_session,
        nombre="Ana",
        apellido="Perez",
        usuario="ana",
        contrasena="clave-segura-123",
        rol=ROL_INSPECTOR,
    )
    with pytest.raises(UsuarioDuplicadoError):
        crear_usuario(
            db_session,
            nombre="Otra",
            apellido="Perez",
            usuario="ana",
            contrasena="clave-segura-123",
            rol=ROL_ADMIN,
        )


def test_crear_usuario_rol_invalido(db_session):
    _sembrar_roles(db_session)
    with pytest.raises(RolInvalidoError):
        crear_usuario(
            db_session,
            nombre="Ana",
            apellido="Perez",
            usuario="ana",
            contrasena="clave-segura-123",
            rol="superadmin",
        )


def test_crear_usuario_contrasena_corta(db_session):
    _sembrar_roles(db_session)
    with pytest.raises(DatosInvalidosError):
        crear_usuario(
            db_session,
            nombre="Ana",
            apellido="Perez",
            usuario="ana",
            contrasena="corta",
            rol=ROL_INSPECTOR,
        )
