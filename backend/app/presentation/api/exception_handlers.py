"""Respuestas de error con forma única para el cliente."""

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def _cuerpo(codigo: str, detalle: str) -> dict[str, str]:
    return {"error": codigo, "detail": detalle}


async def manejar_http(request: Request, exc: HTTPException) -> JSONResponse:
    detalle = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content=_cuerpo("http_error", detalle))


async def manejar_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_cuerpo("validacion", "Los datos enviados no son válidos"),
    )


async def manejar_integridad(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=_cuerpo(
            "conflicto_de_datos",
            "No se pudo guardar: hay un conflicto con datos existentes o referencias inválidas",
        ),
    )


async def manejar_no_controlado(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_cuerpo("error_interno", "Ocurrió un error inesperado"),
    )
