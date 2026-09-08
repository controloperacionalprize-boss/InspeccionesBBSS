"""Bearer: 401 si falta token (Starlette devolvería 403)."""

from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, joinedload

from app.domain.entities import Usuario
from app.domain.roles import ROL_ADMIN
from app.infrastructure.database.models import Usuario as UsuarioModel
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt_handler import decode_access_token

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: Session = Depends(get_session),
) -> Usuario:
    """Valida el JWT y carga usuario/rol vigentes desde la BD."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = payload.get("sub")
    uid = payload.get("uid")
    if subject is None or uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    modelo = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .filter(UsuarioModel.USUARIO == subject, UsuarioModel.ID == int(uid))
        .first()
    )
    if modelo is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o token desactualizado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Usuario(
        id=modelo.ID,
        nombre=modelo.NOMBRE,
        apellido=modelo.APELLIDO,
        usuario=modelo.USUARIO,
        rol=modelo.rol.NOMBRE,
    )


def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.rol != ROL_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return usuario


def require_roles(*roles: str) -> Callable[..., Usuario]:
    def _dependencia(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para esta operación",
            )
        return usuario

    return _dependencia
