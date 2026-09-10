"""Endpoints de fotos adjuntas a Inspecciones (subida múltiple a object storage).

Reglas de robustez:
- Se valida TODO el lote (tipo real por magic bytes + tamaño) antes de subir
  cualquier archivo a S3 -- si un archivo del lote falla, no se sube nada.
- Si falla la subida de un archivo a mitad del lote (error de red, etc.), se
  borran de S3 los que ya se habían subido en esa misma solicitud.
- No se permite agregar ni quitar fotos de una inspección con ELIMINADO=True.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Foto, Inspeccion
from app.infrastructure.database.session import get_session
from app.infrastructure.storage.s3_storage import (
    StorageNoConfiguradoError,
    eliminar_objeto,
    subir_objeto,
    url_firmada,
)
from app.presentation.api.dependencies import get_current_user
from app.presentation.api.rate_limit import limiter
from app.presentation.api.schemas.fotos import FotoRead

router = APIRouter(tags=["Fotos"])

_TAMANO_MAXIMO_BYTES = 8 * 1024 * 1024
_MAX_ARCHIVOS_POR_SUBIDA = 10

# Firma (magic bytes) -> (content-type real, extensión). El content-type que
# manda el cliente no es confiable; el tipo real del archivo sí.
_FIRMAS: list[tuple[bytes, str, str]] = [
    (b"\xff\xd8\xff", "image/jpeg", "jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "png"),
]


def _detectar_tipo_real(contenido: bytes) -> tuple[str, str] | None:
    for firma, content_type, extension in _FIRMAS:
        if contenido.startswith(firma):
            return content_type, extension
    if len(contenido) >= 12 and contenido[0:4] == b"RIFF" and contenido[8:12] == b"WEBP":
        return "image/webp", "webp"
    return None


def _a_lectura(foto: Foto) -> FotoRead:
    return FotoRead(
        ID=foto.ID,
        URL=url_firmada(foto.OBJECT_KEY),
        ORDEN=foto.ORDEN,
        FECHA_SUBIDA=foto.FECHA_SUBIDA,
    )


def _obtener_inspeccion_o_404(session: Session, inspeccion_id: int) -> Inspeccion:
    inspeccion = session.get(Inspeccion, inspeccion_id)
    if inspeccion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inspección no encontrada")
    return inspeccion


@router.get("/inspecciones/{inspeccion_id}/fotos", response_model=list[FotoRead])
def listar_fotos_inspeccion(
    inspeccion_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[FotoRead]:
    _obtener_inspeccion_o_404(session, inspeccion_id)

    fotos = (
        session.query(Foto)
        .filter(Foto.ID_INSPECCION == inspeccion_id)
        .order_by(Foto.ORDEN, Foto.ID)
        .all()
    )
    return [_a_lectura(foto) for foto in fotos]


@router.post(
    "/inspecciones/{inspeccion_id}/fotos",
    response_model=list[FotoRead],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
def subir_fotos_inspeccion(
    request: Request,
    inspeccion_id: int,
    archivos: list[UploadFile],
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[FotoRead]:
    inspeccion = _obtener_inspeccion_o_404(session, inspeccion_id)
    if inspeccion.ELIMINADO:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No se pueden agregar fotos a una inspección eliminada"
        )

    if not archivos:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se recibió ningún archivo")
    if len(archivos) > _MAX_ARCHIVOS_POR_SUBIDA:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Máximo {_MAX_ARCHIVOS_POR_SUBIDA} fotos por subida",
        )

    # Fase 1: validar TODO el lote (lectura acotada + tipo real) antes de
    # subir nada. Si algo falla acá, S3 no se toca.
    validados: list[tuple[bytes, str, str]] = []  # (contenido, content_type, extension)
    for archivo in archivos:
        contenido = archivo.file.read(_TAMANO_MAXIMO_BYTES + 1)
        if len(contenido) > _TAMANO_MAXIMO_BYTES:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"'{archivo.filename}' supera el tamaño máximo de 8MB",
            )
        if not contenido:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, f"'{archivo.filename}' está vacío"
            )

        detectado = _detectar_tipo_real(contenido)
        if detectado is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"'{archivo.filename}' no es una imagen jpg/png/webp válida",
            )
        content_type, extension = detectado
        validados.append((contenido, content_type, extension))

    # Fase 2: subir a S3 y crear las filas. Si algo falla a mitad de camino,
    # se revierte lo ya subido en esta misma solicitud.
    siguiente_orden = session.query(Foto).filter(Foto.ID_INSPECCION == inspeccion_id).count()
    claves_subidas: list[str] = []
    nuevas: list[Foto] = []
    try:
        for contenido, content_type, extension in validados:
            clave = f"inspecciones/{inspeccion_id}/{uuid.uuid4().hex}.{extension}"
            subir_objeto(clave, contenido, content_type)
            claves_subidas.append(clave)

            foto = Foto(
                ID_INSPECCION=inspeccion_id,
                OBJECT_KEY=clave,
                ORDEN=siguiente_orden,
                FECHA_SUBIDA=datetime.now(timezone.utc),
            )
            session.add(foto)
            siguiente_orden += 1
            nuevas.append(foto)

        session.commit()
    except StorageNoConfiguradoError as exc:
        session.rollback()
        for clave in claves_subidas:
            try:
                eliminar_objeto(clave)
            except Exception:
                pass
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    except Exception:
        session.rollback()
        for clave in claves_subidas:
            try:
                eliminar_objeto(clave)
            except Exception:
                pass
        raise

    for foto in nuevas:
        session.refresh(foto)
    return [_a_lectura(foto) for foto in nuevas]


@router.delete("/fotos/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_foto(
    foto_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> None:
    foto = session.get(Foto, foto_id)
    if foto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foto no encontrada")

    if foto.ID_INSPECCION is not None:
        inspeccion = session.get(Inspeccion, foto.ID_INSPECCION)
        if inspeccion is not None and inspeccion.ELIMINADO:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "No se pueden quitar fotos de una inspección eliminada",
            )

    # Se borra primero en BD y recién después en S3: si el commit falla, no
    # queda una referencia rota apuntando a un objeto ya borrado.
    clave = foto.OBJECT_KEY
    session.delete(foto)
    session.commit()

    try:
        eliminar_objeto(clave)
    except Exception:
        # La fila ya no existe en BD (fuente de verdad); si el borrado en S3
        # falla, el objeto queda huérfano pero no hay ninguna referencia
        # rota visible para el usuario.
        pass
