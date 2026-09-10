"""Endpoints de Inspecciones (consultas de Campo / Packing).

Borrado lógico: DELETE marca ELIMINADO=True en vez de borrar la fila. Así se
conserva el histórico para auditoría y las fotos asociadas nunca quedan
huérfanas (no hay cascada física). listar() oculta lo eliminado por defecto;
obtener() por ID siempre lo muestra (para poder pedir el detalle igual).
"""

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.inspecciones.validaciones import (
    InspeccionInvalidaError,
    validar_referencias_inspeccion,
)
from app.infrastructure.database.models import Inspeccion
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin
from app.presentation.api.schemas.inspecciones import InspeccionCreate, InspeccionRead

router = APIRouter(prefix="/inspecciones", tags=["Inspecciones"])


@router.get("", response_model=list[InspeccionRead])
def listar(
    id_empresa: int | None = Query(None),
    id_fundo: int | None = Query(None),
    id_division: int | None = Query(None),
    id_area: int | None = Query(None),
    id_categoria: int | None = Query(None),
    id_subcategoria: int | None = Query(None),
    tipo_consulta: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[Inspeccion]:
    """Lista inspecciones con filtros opcionales de campo, fecha y categoría."""
    consulta = session.query(Inspeccion)

    if not incluir_eliminados:
        consulta = consulta.filter(Inspeccion.ELIMINADO.is_(False))
    if id_empresa is not None:
        consulta = consulta.filter(Inspeccion.ID_EMPRESA == id_empresa)
    if id_fundo is not None:
        consulta = consulta.filter(Inspeccion.ID_FUNDO == id_fundo)
    if id_division is not None:
        consulta = consulta.filter(Inspeccion.ID_DIVISION == id_division)
    if id_area is not None:
        consulta = consulta.filter(Inspeccion.ID_AREA == id_area)
    if id_categoria is not None:
        consulta = consulta.filter(Inspeccion.ID_CATEGORIA == id_categoria)
    if id_subcategoria is not None:
        consulta = consulta.filter(Inspeccion.ID_SUBCATEGORIA == id_subcategoria)
    if tipo_consulta is not None:
        consulta = consulta.filter(Inspeccion.TIPO_CONSULTA == tipo_consulta)
    if fecha_desde is not None:
        consulta = consulta.filter(Inspeccion.FECHA_OBSERVACION >= fecha_desde)
    if fecha_hasta is not None:
        consulta = consulta.filter(Inspeccion.FECHA_OBSERVACION <= fecha_hasta)

    return (
        consulta.order_by(Inspeccion.FECHA_OBSERVACION.desc(), Inspeccion.ID.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{inspeccion_id}", response_model=InspeccionRead)
def obtener(
    inspeccion_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Inspeccion:
    """Devuelve la inspección exista o no ELIMINADO=True: el detalle sigue
    siendo consultable para efectos de auditoría."""
    inspeccion = session.get(Inspeccion, inspeccion_id)
    if inspeccion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inspección no encontrada")
    return inspeccion


@router.post("", response_model=InspeccionRead, status_code=status.HTTP_201_CREATED)
def crear(
    datos: InspeccionCreate,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Inspeccion:
    try:
        validar_referencias_inspeccion(session, datos)
    except InspeccionInvalidaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    inspeccion = Inspeccion(**datos.model_dump())
    session.add(inspeccion)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(inspeccion)
    return inspeccion


@router.put("/{inspeccion_id}", response_model=InspeccionRead)
def actualizar(
    inspeccion_id: int,
    datos: InspeccionCreate,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Inspeccion:
    inspeccion = session.get(Inspeccion, inspeccion_id)
    if inspeccion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inspección no encontrada")
    if inspeccion.ELIMINADO:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No se puede editar una inspección eliminada"
        )

    try:
        validar_referencias_inspeccion(session, datos)
    except InspeccionInvalidaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    for campo, valor in datos.model_dump().items():
        setattr(inspeccion, campo, valor)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(inspeccion)
    return inspeccion


@router.delete("/{inspeccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    inspeccion_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(require_admin),
) -> None:
    """Borrado lógico: no se toca la fila ni sus fotos, solo se marca."""
    inspeccion = session.get(Inspeccion, inspeccion_id)
    if inspeccion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Inspección no encontrada")
    if inspeccion.ELIMINADO:
        return

    inspeccion.ELIMINADO = True
    inspeccion.FECHA_ELIMINACION = datetime.now(timezone.utc)
    session.commit()
