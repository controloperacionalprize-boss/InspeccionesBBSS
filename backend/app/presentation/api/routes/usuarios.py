from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.usuarios.gestionar import (
    actualizar_usuario,
    crear_usuario,
    listar_usuarios,
    obtener_usuario,
)
from app.domain.exceptions import (
    DatosInvalidosError,
    RecursoNoEncontradoError,
    RolInvalidoError,
    UsuarioDuplicadoError,
)
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import require_admin
from app.presentation.api.schemas.usuarios import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


def _http_negocio(exc: Exception) -> HTTPException:
    if isinstance(exc, UsuarioDuplicadoError):
        return HTTPException(status.HTTP_409_CONFLICT, str(exc))
    if isinstance(exc, RolInvalidoError):
        return HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    if isinstance(exc, RecursoNoEncontradoError):
        return HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    if isinstance(exc, DatosInvalidosError):
        return HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    return HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


@router.get("", response_model=list[UsuarioRead])
def listar(
    session: Session = Depends(get_session),
    _admin=Depends(require_admin),
) -> list[UsuarioRead]:
    return [
        UsuarioRead(
            id=u.id, nombre=u.nombre, apellido=u.apellido, usuario=u.usuario, rol=u.rol, dni=u.dni
        )
        for u in listar_usuarios(session)
    ]


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear(
    datos: UsuarioCreate,
    session: Session = Depends(get_session),
    _admin=Depends(require_admin),
) -> UsuarioRead:
    try:
        u = crear_usuario(
            session,
            nombre=datos.nombre,
            apellido=datos.apellido,
            usuario=datos.usuario,
            contrasena=datos.contrasena,
            rol=datos.rol,
            dni=datos.dni,
        )
    except (UsuarioDuplicadoError, RolInvalidoError, RecursoNoEncontradoError, DatosInvalidosError) as ext:
        raise _http_negocio(ext) from ext
    return UsuarioRead(
        id=u.id, nombre=u.nombre, apellido=u.apellido, usuario=u.usuario, rol=u.rol, dni=u.dni
    )


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener(
    usuario_id: int,
    session: Session = Depends(get_session),
    _admin=Depends(require_admin),
) -> UsuarioRead:
    try:
        u = obtener_usuario(session, usuario_id)
    except RecursoNoEncontradoError as ext:
        raise _http_negocio(ext) from ext
    return UsuarioRead(
        id=u.id, nombre=u.nombre, apellido=u.apellido, usuario=u.usuario, rol=u.rol, dni=u.dni
    )


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar(
    usuario_id: int,
    datos: UsuarioUpdate,
    session: Session = Depends(get_session),
    _admin=Depends(require_admin),
) -> UsuarioRead:
    try:
        u = actualizar_usuario(
            session,
            usuario_id,
            nombre=datos.nombre,
            apellido=datos.apellido,
            rol=datos.rol,
            dni=datos.dni,
            contrasena=datos.contrasena,
        )
    except (RolInvalidoError, RecursoNoEncontradoError, DatosInvalidosError) as ext:
        raise _http_negocio(ext) from ext
    return UsuarioRead(
        id=u.id, nombre=u.nombre, apellido=u.apellido, usuario=u.usuario, rol=u.rol, dni=u.dni
    )
