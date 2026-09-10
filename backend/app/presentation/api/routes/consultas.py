"""Endpoints de Consultas (registro móvil + seguimiento web).

Borrado lógico: ver docstring de routes/inspecciones.py, mismo criterio.
"""

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.catalogos.validaciones import (
    ReferenciaCatalogoInvalidaError,
    validar_empresa_fundo_division_area,
)
from app.infrastructure.database.models import Consulta
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin
from app.presentation.api.schemas.consultas import (
    ConsultaCreate,
    ConsultaRead,
    ConsultaUpdate,
)

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.get("", response_model=list[ConsultaRead])
def listar(
    id_empresa: int | None = Query(None),
    id_fundo: int | None = Query(None),
    id_division: int | None = Query(None),
    id_area: int | None = Query(None),
    dni_trabajador: str | None = Query(None),
    tipo_consulta: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[Consulta]:
    consulta = session.query(Consulta)

    if not incluir_eliminados:
        consulta = consulta.filter(Consulta.ELIMINADO.is_(False))
    if id_empresa is not None:
        consulta = consulta.filter(Consulta.ID_EMPRESA == id_empresa)
    if id_fundo is not None:
        consulta = consulta.filter(Consulta.ID_FUNDO == id_fundo)
    if id_division is not None:
        consulta = consulta.filter(Consulta.ID_DIVISION == id_division)
    if id_area is not None:
        consulta = consulta.filter(Consulta.ID_AREA == id_area)
    if dni_trabajador is not None:
        consulta = consulta.filter(Consulta.DNI_TRABAJADOR == dni_trabajador)
    if tipo_consulta is not None:
        consulta = consulta.filter(Consulta.TIPO_CONSULTA == tipo_consulta)
    if fecha_desde is not None:
        consulta = consulta.filter(Consulta.FECHA_CONSULTA >= fecha_desde)
    if fecha_hasta is not None:
        consulta = consulta.filter(Consulta.FECHA_CONSULTA <= fecha_hasta)

    return (
        consulta.order_by(Consulta.FECHA_CONSULTA.desc(), Consulta.ID.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{consulta_id}", response_model=ConsultaRead)
def obtener(
    consulta_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Consulta:
    consulta = session.get(Consulta, consulta_id)
    if consulta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Consulta no encontrada")
    return consulta


@router.post("", response_model=ConsultaRead, status_code=status.HTTP_201_CREATED)
def crear(
    datos: ConsultaCreate,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Consulta:
    try:
        validar_empresa_fundo_division_area(session, datos)
    except ReferenciaCatalogoInvalidaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    consulta = Consulta(**datos.model_dump())
    session.add(consulta)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(consulta)
    return consulta


@router.put("/{consulta_id}", response_model=ConsultaRead)
def actualizar(
    consulta_id: int,
    datos: ConsultaUpdate,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Consulta:
    """No permite tocar RESPUESTA_INMEDIATA: se captura en campo y queda fija."""
    consulta = session.get(Consulta, consulta_id)
    if consulta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Consulta no encontrada")
    if consulta.ELIMINADO:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No se puede editar una consulta eliminada"
        )

    try:
        validar_empresa_fundo_division_area(session, datos)
    except ReferenciaCatalogoInvalidaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    for campo, valor in datos.model_dump().items():
        setattr(consulta, campo, valor)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(consulta)
    return consulta


@router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    consulta_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(require_admin),
) -> None:
    """Borrado lógico: conserva el registro para auditoría."""
    consulta = session.get(Consulta, consulta_id)
    if consulta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Consulta no encontrada")
    if consulta.ELIMINADO:
        return

    consulta.ELIMINADO = True
    consulta.FECHA_ELIMINACION = datetime.now(timezone.utc)
    session.commit()
