"""Endpoints de Indumentaria (entregas de EPP/uniforme a trabajadores).

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
    aplicar_tipo_consulta,
    validar_empresa_fundo_division_area,
)
from app.application.exportacion.excel import CONTENT_TYPE_XLSX, libro_excel, nombre_archivo
from app.infrastructure.database.models import Area, Division, Empresa, Fundo, Indumentaria
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin
from app.presentation.api.tiempo_real import avisar
from app.presentation.api.schemas.indumentaria import IndumentariaCreate, IndumentariaRead

router = APIRouter(prefix="/indumentaria", tags=["Indumentaria"])


def _filtrar(
    session: Session,
    id_empresa: int | None,
    id_fundo: int | None,
    id_division: int | None,
    id_area: int | None,
    dni_trabajador: str | None,
    tipo: str | None,
    tipo_consulta: str | None,
    fecha_desde: date | None,
    fecha_hasta: date | None,
    incluir_eliminados: bool,
):
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
    if tipo_consulta is not None:
        consulta = consulta.filter(Indumentaria.TIPO_CONSULTA == tipo_consulta)
    if fecha_desde is not None:
        consulta = consulta.filter(Indumentaria.FECHA_ENTREGA >= fecha_desde)
    if fecha_hasta is not None:
        consulta = consulta.filter(Indumentaria.FECHA_ENTREGA <= fecha_hasta)
    return consulta


@router.get("", response_model=list[IndumentariaRead])
def listar(
    response: Response,
    id_empresa: int | None = Query(None),
    id_fundo: int | None = Query(None),
    id_division: int | None = Query(None),
    id_area: int | None = Query(None),
    dni_trabajador: str | None = Query(None),
    tipo: str | None = Query(None),
    tipo_consulta: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[Indumentaria]:
    consulta = _filtrar(
        session,
        id_empresa,
        id_fundo,
        id_division,
        id_area,
        dni_trabajador,
        tipo,
        tipo_consulta,
        fecha_desde,
        fecha_hasta,
        incluir_eliminados,
    )

    # Total para la paginación del cliente, con los mismos filtros y sin traer filas.
    response.headers["X-Total-Count"] = str(consulta.order_by(None).count())

    return (
        consulta.order_by(Indumentaria.FECHA_ENTREGA.desc(), Indumentaria.ID.desc())
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
    tipo: str | None = Query(None),
    tipo_consulta: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> StreamingResponse:
    """Exporta a Excel las entregas de indumentaria que cumplen los mismos filtros del listado."""
    filas = (
        _filtrar(
            session,
            id_empresa,
            id_fundo,
            id_division,
            id_area,
            dni_trabajador,
            tipo,
            tipo_consulta,
            fecha_desde,
            fecha_hasta,
            incluir_eliminados,
        )
        .order_by(Indumentaria.FECHA_ENTREGA.desc(), Indumentaria.ID.desc())
        .all()
    )

    nombre_empresa = {e.ID: e.NOMBRE for e in session.query(Empresa)}
    nombre_fundo = {f.ID: f.NOMBRE for f in session.query(Fundo)}
    nombre_division = {d.ID: d.NOMBRE for d in session.query(Division)}
    nombre_area = {a.ID: a.NOMBRE for a in session.query(Area)}

    encabezados = [
        "ID",
        "Fecha de entrega",
        "Tipo",
        "Empresa",
        "Fundo",
        "División",
        "Área",
        "DNI trabajador",
        "Apellidos y nombres",
        "Ítem",
        "Cantidad",
        "Firma",
        "Responsable de registro",
        "Eliminado",
    ]
    cuerpo = [
        [
            i.ID,
            i.FECHA_ENTREGA,
            i.TIPO_CONSULTA,
            nombre_empresa.get(i.ID_EMPRESA, i.ID_EMPRESA),
            nombre_fundo.get(i.ID_FUNDO, i.ID_FUNDO),
            nombre_division.get(i.ID_DIVISION, i.ID_DIVISION),
            nombre_area.get(i.ID_AREA, i.ID_AREA),
            i.DNI_TRABAJADOR,
            i.APELLIDOS_NOMBRES,
            i.TIPO,
            i.CANTIDAD,
            i.FIRMA,
            i.RESPONSABLE_REGISTRO,
            "Sí" if i.ELIMINADO else "No",
        ]
        for i in filas
    ]
    contenido = libro_excel("Indumentaria", encabezados, cuerpo)
    archivo = nombre_archivo("indumentaria")
    return StreamingResponse(
        BytesIO(contenido),
        media_type=CONTENT_TYPE_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{archivo}"'},
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

    entrega = Indumentaria(**aplicar_tipo_consulta(session, datos.model_dump()))
    session.add(entrega)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    avisar("indumentaria")
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

    for campo, valor in aplicar_tipo_consulta(session, datos.model_dump()).items():
        setattr(entrega, campo, valor)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    avisar("indumentaria")
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
    avisar("indumentaria")
