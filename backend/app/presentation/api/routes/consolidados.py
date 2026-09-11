"""Lecturas agregadas para no obligar al cliente a hacer muchas peticiones.

- /catalogos: los seis maestros en una sola respuesta (el cliente la cachea).
- /resumen: conteos del inicio calculados en SQL, en vez de descargar filas.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.infrastructure.database.models import (
    Area,
    Categoria,
    Consulta,
    Division,
    Empresa,
    Fundo,
    Indumentaria,
    Inspeccion,
    Subcategoria,
)
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user
from app.presentation.api.schemas.catalogos import (
    AreaRead,
    CategoriaRead,
    DivisionRead,
    EmpresaRead,
    FundoRead,
    SubcategoriaRead,
)
from app.presentation.api.schemas.consolidados import CatalogosRead, InspeccionesPorTipo, ResumenRead

router = APIRouter(tags=["Consolidados"])


@router.get("/catalogos", response_model=CatalogosRead)
def catalogos(
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> CatalogosRead:
    def todos(modelo, esquema):
        return [esquema.model_validate(fila) for fila in session.query(modelo).order_by(modelo.NOMBRE).all()]

    return CatalogosRead(
        empresas=todos(Empresa, EmpresaRead),
        fundos=todos(Fundo, FundoRead),
        divisiones=todos(Division, DivisionRead),
        areas=todos(Area, AreaRead),
        categorias=todos(Categoria, CategoriaRead),
        subcategorias=todos(Subcategoria, SubcategoriaRead),
    )


def _vacio(columna):
    return or_(columna.is_(None), func.trim(columna) == "")


@router.get("/resumen", response_model=ResumenRead)
def resumen(
    desde: date = Query(..., description="Inicio del periodo (p. ej. primer día del mes, en hora local)"),
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> ResumenRead:
    del_periodo = (Inspeccion.ELIMINADO.is_(False), Inspeccion.FECHA_OBSERVACION >= desde)

    por_tipo = dict(
        session.query(Inspeccion.TIPO_CONSULTA, func.count(Inspeccion.ID))
        .filter(*del_periodo)
        .group_by(Inspeccion.TIPO_CONSULTA)
        .all()
    )
    sin_accion = (
        session.query(func.count(Inspeccion.ID))
        .filter(*del_periodo, _vacio(Inspeccion.ACCION_CORRECTIVA))
        .scalar()
    )
    por_responder = (
        session.query(func.count(Consulta.ID))
        .filter(Consulta.ELIMINADO.is_(False), _vacio(Consulta.RESPUESTA_POSTERIOR))
        .scalar()
    )
    entregas, unidades = (
        session.query(func.count(Indumentaria.ID), func.coalesce(func.sum(Indumentaria.CANTIDAD), 0))
        .filter(Indumentaria.ELIMINADO.is_(False), Indumentaria.FECHA_ENTREGA >= desde)
        .one()
    )

    return ResumenRead(
        inspecciones=sum(por_tipo.values()),
        inspecciones_por_tipo=InspeccionesPorTipo(
            campo=por_tipo.get("Campo", 0),
            packing=por_tipo.get("Packing", 0),
            sin_tipo=sum(v for k, v in por_tipo.items() if k not in ("Campo", "Packing")),
        ),
        inspecciones_sin_accion=sin_accion or 0,
        consultas_por_responder=por_responder or 0,
        entregas=entregas or 0,
        unidades_entregadas=int(unidades or 0),
    )
