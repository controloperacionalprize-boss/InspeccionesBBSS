from sqlalchemy.orm import Session, joinedload

from app.domain.entities import Usuario
from app.domain.exceptions import CredencialesInvalidasError
from app.infrastructure.database.models import Usuario as UsuarioModel
from app.infrastructure.security.password_hasher import verify_password
from app.infrastructure.security.timing import HASH_TIMING_DUMMY


def login_usuario(session: Session, usuario: str, contrasena: str) -> Usuario:
    """Valida usuario y contraseña. Lanza CredencialesInvalidasError si fallan."""
    modelo = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .filter(UsuarioModel.USUARIO == usuario)
        .first()
    )

    hash_a_verificar = modelo.PASSWORD_HASH if modelo is not None else HASH_TIMING_DUMMY
    credenciales_validas = modelo is not None and verify_password(contrasena, hash_a_verificar)

    if not credenciales_validas:
        raise CredencialesInvalidasError("Usuario o contraseña incorrectos")

    return Usuario(
        id=modelo.ID,
        nombre=modelo.NOMBRE,
        apellido=modelo.APELLIDO,
        usuario=modelo.USUARIO,
        rol=modelo.rol.NOMBRE,
    )
