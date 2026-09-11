"""Endpoints de Consultas (registro móvil + seguimiento web).

Borrado lógico: ver docstring de routes/inspecciones.py, mismo criterio.
"""

from datetime import date, datetime, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.catalogos.validaciones import (
    ReferenciaCatalogoInvalidaError,
    validar_empresa_fundo_division_area,
)
from app.application.exportacion.excel import CONTENT_TYPE_XLSX, libro_excel, nombre_archivo
from app.infrastructure.database.models import Area, Consulta, Division, Empresa, Fundo
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin
from app.presentation.api.schemas.consultas import (
    ConsultaCreate,
    ConsultaRead,
    ConsultaUpdate,
)

router = APIRouter(prefix="/consultas", tags=["Consultas"])


def _filtrar(
    session: Session,
    id_empresa: int | None,
    id_fundo: int | None,
    id_division: int | None,
    id_area: int | None,
    dni_trabajador: str | None,
    tipo_consulta: str | None,
    fecha_desde: date | None,
    fecha_hasta: date | None,
    incluir_eliminados: bool,
):
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
    return consulta


@router.get("", response_model=list[ConsultaRead])
def listar(
    response: Response,
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
    consulta = _filtrar(
        session,
        id_empresa,
        id_fundo,
        id_division,
        id_area,
        dni_trabajador,
        tipo_consulta,
        fecha_desde,
        fecha_hasta,
        incluir_eliminados,
    )

    # Total para la paginación del cliente, con los mismos filtros y sin traer filas.
    response.headers["X-Total-Count"] = str(consulta.order_by(None).count())

    return (
        consulta.order_by(Consulta.FECHA_CONSULTA.desc(), Consulta.ID.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/exportar")
def exportar(
    id_empresa: int | None = Query(None),
    id_fundo: int | None = Query(None),
    id_division: int | None = Query(None),
    id_area: int | None = Query(None),
    dni_trabajador: str | None = Query(None),
    tipo_consulta: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> StreamingResponse:
    """Exporta a Excel las consultas que cumplen los mismos filtros del listado."""
    filas = (
        _filtrar(
            session,
            id_empresa,
            id_fundo,
            id_division,
            id_area,
            dni_trabajador,
            tipo_consulta,
            fecha_desde,
            fecha_hasta,
            incluir_eliminados,
        )
        .order_by(Consulta.FECHA_CONSULTA.desc(), Consulta.ID.desc())
        .all()
    )

    nombre_empresa = {e.ID: e.NOMBRE for e in session.query(Empresa)}
    nombre_fundo = {f.ID: f.NOMBRE for f in session.query(Fundo)}
    nombre_division = {d.ID: d.NOMBRE for d in session.query(Division)}
    nombre_area = {a.ID: a.NOMBRE for a in session.query(Area)}

    encabezados = [
        "ID",
        "Fecha",
        "Tipo",
        "Empresa",
        "Fundo",
        "División",
        "Área",
        "DNI trabajador",
        "Apellidos y nombres",
        "Descripción",
        "Área responsable",
        "Respuesta inmediata",
        "Respuesta posterior",
        "Eliminado",
    ]
    cuerpo = [
        [
            c.ID,
            c.FECHA_CONSULTA,
            c.TIPO_CONSULTA,
            nombre_empresa.get(c.ID_EMPRESA, c.ID_EMPRESA),
            nombre_fundo.get(c.ID_FUNDO, c.ID_FUNDO),
            nombre_division.get(c.ID_DIVISION, c.ID_DIVISION),
            nombre_area.get(c.ID_AREA, c.ID_AREA),
            c.DNI_TRABAJADOR,
            c.APELLIDOS_NOMBRES,
            c.DESCRIPCION,
            c.AREA_RESPONSABLE,
            c.RESPUESTA_INMEDIATA,
            c.RESPUESTA_POSTERIOR,
            "Sí" if c.ELIMINADO else "No",
        ]
        for c in filas
    ]
    contenido = libro_excel("Consultas", encabezados, cuerpo)
    archivo = nombre_archivo("consultas")
    return StreamingResponse(
        BytesIO(contenido),
        media_type=CONTENT_TYPE_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{archivo}"'},
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
