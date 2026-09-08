from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, joinedload

from app.application.auth.login_usuario import login_usuario
from app.domain.entities import Usuario
from app.domain.exceptions import CredencialesInvalidasError
from app.infrastructure.database.models import Usuario as UsuarioModel
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt_handler import create_access_token
from app.presentation.api.dependencies import get_current_user
from app.presentation.api.rate_limit import limiter
from app.presentation.api.schemas.auth import LoginRequest, LoginResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    datos: LoginRequest,
    session: Session = Depends(get_session),
) -> LoginResponse:
    """Autentica a un usuario mediante usuario y contraseña, devolviendo un JWT."""
    try:
        usuario = login_usuario(session, datos.usuario, datos.contrasena)
    except CredencialesInvalidasError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    token = create_access_token(
        subject=usuario.usuario,
        extra_claims={"uid": usuario.id, "rol": usuario.rol},
    )

    return LoginResponse(
        access_token=token,
        usuario=UsuarioResponse(
            id=usuario.id,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            usuario=usuario.usuario,
            rol=usuario.rol,
        ),
    )


@router.get("/me", response_model=UsuarioResponse)
def me(
    usuario_actual: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UsuarioResponse:
    """Perfil actual desde la BD."""
    modelo = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .filter(UsuarioModel.USUARIO == usuario_actual.usuario)
        .first()
    )
    if modelo is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return UsuarioResponse(
        id=modelo.ID,
        nombre=modelo.NOMBRE,
        apellido=modelo.APELLIDO,
        usuario=modelo.USUARIO,
        rol=modelo.rol.NOMBRE,
    )
