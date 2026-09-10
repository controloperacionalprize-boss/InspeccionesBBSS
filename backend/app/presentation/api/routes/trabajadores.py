"""Búsqueda de trabajadores por DNI en el maestro de personal (RDS externa).

Usado por los formularios de Consultas e Indumentaria para autocompletar
APELLIDOS_NOMBRES a partir de DNI_TRABAJADOR.
"""

import re

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.infrastructure.external.rrhh_client import (
    RrhhNoConfiguradoError,
    buscar_trabajador_por_dni,
)
from app.presentation.api.dependencies import get_current_user
from app.presentation.api.rate_limit import limiter
from app.presentation.api.schemas.trabajadores import TrabajadorRead

router = APIRouter(prefix="/trabajadores", tags=["Trabajadores"])

_DNI_VALIDO = re.compile(r"^\d{8}$")


@router.get("/{dni}", response_model=TrabajadorRead)
@limiter.limit("60/minute")
def obtener_por_dni(
    request: Request,
    dni: str,
    _usuario=Depends(get_current_user),
) -> TrabajadorRead:
    if not _DNI_VALIDO.match(dni):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "DNI inválido: debe tener 8 dígitos")

    try:
        trabajador = buscar_trabajador_por_dni(dni)
    except RrhhNoConfiguradoError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    if trabajador is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trabajador no encontrado")

    return TrabajadorRead(
        DNI=trabajador.dni,
        APELLIDOS_NOMBRES=trabajador.apellidos_nombres,
        EMPRESA=trabajador.empresa,
        CARGO=trabajador.cargo,
        VIGENTE=trabajador.vigente,
    )
