"""Endpoints de Indumentaria (entregas de EPP/uniforme a trabajadores).

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
from app.infrastructure.database.models import Indumentaria
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin
from app.presentation.api.schemas.indumentaria import IndumentariaCreate, IndumentariaRead

router = APIRouter(prefix="/indumentaria", tags=["Indumentaria"])


@router.get("", response_model=list[IndumentariaRead])
def listar(
    id_empresa: int | None = Query(None),
    id_fundo: int | None = Query(None),
    id_division: int | None = Query(None),
    id_area: int | None = Query(None),
    dni_trabajador: str | None = Query(None),
    tipo: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[Indumentaria]:
    consulta = session.query(Indumentaria)

    if not incluir_eliminados:
        consulta = consulta.filter(Indumentaria.ELIMINADO.is_(False))
    if id_empresa is not None:
        consulta = consulta.filter(Indumentaria.ID_EMPRESA == id_empresa)
    if id_fundo is not None:
        consulta = consulta.filter(Indumentaria.ID_FUNDO == id_fundo)
    if id_division is not None:
        consulta = consulta.filter(Indumentaria.ID_DIVISION == id_division)
    if id_area is not None:
        consulta = consulta.filter(Indumentaria.ID_AREA == id_area)
    if dni_trabajador is not None:
        consulta = consulta.filter(Indumentaria.DNI_TRABAJADOR == dni_trabajador)
    if tipo is not None:
        consulta = consulta.filter(Indumentaria.TIPO == tipo)
    if fecha_desde is not None:
        consulta = consulta.filter(Indumentaria.FECHA_ENTREGA >= fecha_desde)
    if fecha_hasta is not None:
        consulta = consulta.filter(Indumentaria.FECHA_ENTREGA <= fecha_hasta)

    return (
        consulta.order_by(Indumentaria.FECHA_ENTREGA.desc(), Indumentaria.ID.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{indumentaria_id}", response_model=IndumentariaRead)
def obtener(
    indumentaria_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Indumentaria:
    entrega = session.get(Indumentaria, indumentaria_id)
    if entrega is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entrega de indumentaria no encontrada")
    return entrega


@router.post("", response_model=IndumentariaRead, status_code=status.HTTP_201_CREATED)
def crear(
    datos: IndumentariaCreate,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Indumentaria:
    try:
        validar_empresa_fundo_division_area(session, datos)
    except ReferenciaCatalogoInvalidaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    entrega = Indumentaria(**datos.model_dump())
    session.add(entrega)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(entrega)
    return entrega


@router.put("/{indumentaria_id}", response_model=IndumentariaRead)
def actualizar(
    indumentaria_id: int,
    datos: IndumentariaCreate,
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> Indumentaria:
    entrega = session.get(Indumentaria, indumentaria_id)
    if entrega is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entrega de indumentaria no encontrada")
    if entrega.ELIMINADO:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "No se puede editar una entrega eliminada"
        )

    try:
        validar_empresa_fundo_division_area(session, datos)
    except ReferenciaCatalogoInvalidaError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    for campo, valor in datos.model_dump().items():
        setattr(entrega, campo, valor)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    session.refresh(entrega)
    return entrega


@router.delete("/{indumentaria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    indumentaria_id: int,
    session: Session = Depends(get_session),
    _usuario=Depends(require_admin),
) -> None:
    """Borrado lógico: conserva el registro para auditoría."""
    entrega = session.get(Indumentaria, indumentaria_id)
    if entrega is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entrega de indumentaria no encontrada")
    if entrega.ELIMINADO:
        return

    entrega.ELIMINADO = True
    entrega.FECHA_ELIMINACION = datetime.now(timezone.utc)
    session.commit()
