from sqlalchemy.orm import Session, joinedload

from app.domain.entities import Usuario
from app.domain.exceptions import (
    DatosInvalidosError,
    RecursoNoEncontradoError,
    RolInvalidoError,
    UsuarioDuplicadoError,
)
from app.domain.roles import ROLES_VALIDOS
from app.infrastructure.database.models import Rol
from app.infrastructure.database.models import Usuario as UsuarioModel
from app.infrastructure.security.password_hasher import hash_password


def _rol_por_nombre(session: Session, nombre: str) -> Rol:
    if nombre not in ROLES_VALIDOS:
        raise RolInvalidoError(f"Rol inválido: {nombre}")
    rol = session.query(Rol).filter(Rol.NOMBRE == nombre).first()
    if rol is None:
        raise RecursoNoEncontradoError("El rol no existe en la base de datos")
    return rol


def _a_entidad(modelo: UsuarioModel) -> Usuario:
    return Usuario(
        id=modelo.ID,
        nombre=modelo.NOMBRE,
        apellido=modelo.APELLIDO,
        usuario=modelo.USUARIO,
        rol=modelo.rol.NOMBRE,
        dni=modelo.DNI,
    )


def crear_usuario(
    session: Session,
    *,
    nombre: str,
    apellido: str,
    usuario: str,
    contrasena: str,
    rol: str,
    dni: str | None = None,
) -> Usuario:
    if len(contrasena) < 8:
        raise DatosInvalidosError("La contraseña debe tener al menos 8 caracteres")
    if session.query(UsuarioModel).filter(UsuarioModel.USUARIO == usuario).first():
        raise UsuarioDuplicadoError("El nombre de usuario ya existe")

    rol_modelo = _rol_por_nombre(session, rol)
    modelo = UsuarioModel(
        NOMBRE=nombre,
        APELLIDO=apellido,
        DNI=dni,
        USUARIO=usuario,
        PASSWORD_HASH=hash_password(contrasena),
        ID_ROL=rol_modelo.ID,
    )
    session.add(modelo)
    session.commit()
    session.refresh(modelo)
    modelo = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .filter(UsuarioModel.ID == modelo.ID)
        .one()
    )
    return _a_entidad(modelo)


def listar_usuarios(session: Session) -> list[Usuario]:
    filas = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .order_by(UsuarioModel.ID)
        .all()
    )
    return [_a_entidad(m) for m in filas]


def obtener_usuario(session: Session, usuario_id: int) -> Usuario:
    modelo = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .filter(UsuarioModel.ID == usuario_id)
        .first()
    )
    if modelo is None:
        raise RecursoNoEncontradoError("Usuario no encontrado")
    return _a_entidad(modelo)


def actualizar_usuario(
    session: Session,
    usuario_id: int,
    *,
    nombre: str,
    apellido: str,
    rol: str,
    dni: str | None = None,
    contrasena: str | None = None,
) -> Usuario:
    modelo = session.get(UsuarioModel, usuario_id)
    if modelo is None:
        raise RecursoNoEncontradoError("Usuario no encontrado")

    rol_modelo = _rol_por_nombre(session, rol)
    modelo.NOMBRE = nombre
    modelo.APELLIDO = apellido
    modelo.DNI = dni
    modelo.ID_ROL = rol_modelo.ID
    if contrasena:
        if len(contrasena) < 8:
            raise DatosInvalidosError("La contraseña debe tener al menos 8 caracteres")
        modelo.PASSWORD_HASH = hash_password(contrasena)

    session.commit()
    return obtener_usuario(session, usuario_id)
