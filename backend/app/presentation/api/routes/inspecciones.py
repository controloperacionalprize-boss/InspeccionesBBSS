"""Endpoints de Inspecciones (consultas de Campo / Packing).

Borrado lógico: DELETE marca ELIMINADO=True en vez de borrar la fila. Así se
conserva el histórico para auditoría y las fotos asociadas nunca quedan
huérfanas (no hay cascada física). listar() oculta lo eliminado por defecto;
obtener() por ID siempre lo muestra (para poder pedir el detalle igual).
"""

from datetime import date, datetime, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.catalogos.validaciones import aplicar_tipo_consulta
from app.application.exportacion.excel import CONTENT_TYPE_XLSX, libro_excel, nombre_archivo
from app.application.inspecciones.validaciones import (
    InspeccionInvalidaError,
    validar_referencias_inspeccion,
)
from app.infrastructure.database.models import (
    Area,
    Categoria,
    Division,
    Empresa,
    Fundo,
    Inspeccion,
    Subcategoria,
)
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin
from app.presentation.api.tiempo_real import avisar
from app.presentation.api.schemas.inspecciones import InspeccionCreate, InspeccionRead

router = APIRouter(prefix="/inspecciones", tags=["Inspecciones"])


def _filtrar(
    session: Session,
    id_empresa: int | None,
    id_fundo: int | None,
    id_division: int | None,
    id_area: int | None,
    id_categoria: int | None,
    id_subcategoria: int | None,
    tipo_consulta: str | None,
    fecha_desde: date | None,
    fecha_hasta: date | None,
    incluir_eliminados: bool,
):
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
    return consulta


@router.get("", response_model=list[InspeccionRead])
def listar(
    response: Response,
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
    consulta = _filtrar(
        session,
        id_empresa,
        id_fundo,
        id_division,
        id_area,
        id_categoria,
        id_subcategoria,
        tipo_consulta,
        fecha_desde,
        fecha_hasta,
        incluir_eliminados,
    )

    # Total para la paginación del cliente, con los mismos filtros y sin traer filas.
    response.headers["X-Total-Count"] = str(consulta.order_by(None).count())

    return (
        consulta.order_by(Inspeccion.FECHA_OBSERVACION.desc(), Inspeccion.ID.desc())
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
    id_categoria: int | None = Query(None),
    id_subcategoria: int | None = Query(None),
    tipo_consulta: str | None = Query(None),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    incluir_eliminados: bool = Query(False),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> StreamingResponse:
    """Exporta a Excel las inspecciones que cumplen los mismos filtros del listado."""
    filas = (
        _filtrar(
            session,
            id_empresa,
            id_fundo,
            id_division,
            id_area,
            id_categoria,
            id_subcategoria,
            tipo_consulta,
            fecha_desde,
            fecha_hasta,
            incluir_eliminados,
        )
        .order_by(Inspeccion.FECHA_OBSERVACION.desc(), Inspeccion.ID.desc())
        .all()
    )

    nombre_empresa = {e.ID: e.NOMBRE for e in session.query(Empresa)}
    nombre_fundo = {f.ID: f.NOMBRE for f in session.query(Fundo)}
    nombre_division = {d.ID: d.NOMBRE for d in session.query(Division)}
    nombre_area = {a.ID: a.NOMBRE for a in session.query(Area)}
    nombre_categoria = {c.ID: c.NOMBRE for c in session.query(Categoria)}
    nombre_subcategoria = {s.ID: s.NOMBRE for s in session.query(Subcategoria)}

    encabezados = [
        "ID",
        "Fecha",
        "Tipo",
        "Empresa",
        "Fundo",
        "División",
        "Área",
        "Categoría",
        "Subcategoría",
        "Descripción",
        "Acción correctiva",
        "Plazo de levantamiento",
        "Eliminado",
    ]
    cuerpo = [
        [
            i.ID,
            i.FECHA_OBSERVACION,
            i.TIPO_CONSULTA,
            nombre_empresa.get(i.ID_EMPRESA, i.ID_EMPRESA),
            nombre_fundo.get(i.ID_FUNDO, i.ID_FUNDO),
            nombre_division.get(i.ID_DIVISION, i.ID_DIVISION),
            nombre_area.get(i.ID_AREA, i.ID_AREA),
            nombre_categoria.get(i.ID_CATEGORIA, i.ID_CATEGORIA),
            nombre_subcategoria.get(i.ID_SUBCATEGORIA, i.ID_SUBCATEGORIA),
            i.DESCRIPCION,
            i.ACCION_CORRECTIVA,
            i.PLAZO_LEVANTAMIENTO,
            "Sí" if i.ELIMINADO else "No",
        ]
        for i in filas
    ]
    contenido = libro_excel("Inspecciones", encabezados, cuerpo)
    archivo = nombre_archivo("inspecciones")
    return StreamingResponse(
        BytesIO(contenido),
        media_type=CONTENT_TYPE_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{archivo}"'},
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

    inspeccion = Inspeccion(**aplicar_tipo_consulta(session, datos.model_dump()))
    session.add(inspeccion)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    avisar("inspecciones")
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

    for campo, valor in aplicar_tipo_consulta(session, datos.model_dump()).items():
        setattr(inspeccion, campo, valor)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    avisar("inspecciones")
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
    avisar("inspecciones")
