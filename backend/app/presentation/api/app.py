from contextlib import asynccontextmanager
import asyncio
import logging
from logging import Logger

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from app.infrastructure.config import settings
from app.presentation.api.exception_handlers import (
    manejar_http,
    manejar_integridad,
    manejar_no_controlado,
    manejar_validacion,
)
from app.presentation.api.security_headers import SecurityHeadersMiddleware
from app.presentation.api.rate_limit import limiter
from app.presentation.api.router import api_router
from app.presentation.api.routes import health
from app.presentation.api.tiempo_real import hub


def configurar_logging() -> Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return logging.getLogger("consultar_campo")


@asynccontextmanager
async def lifespan(_application: FastAPI):
    hub.asignar_loop(asyncio.get_running_loop())
    yield
    await hub.cerrar_todas()


def create_app() -> FastAPI:
    """FastAPI application factory."""
    logger = configurar_logging()
    docs_url = None if settings.es_produccion else "/docs"
    redoc_url = None if settings.es_produccion else "/redoc"

    application = FastAPI(
        title="Consultar Campo – Packing",
        description="API base del sistema Consultar Campo – Packing",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=None if settings.es_produccion else "/openapi.json",
        lifespan=lifespan,
    )
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_exception_handler(HTTPException, manejar_http)
    application.add_exception_handler(RequestValidationError, manejar_validacion)
    application.add_exception_handler(IntegrityError, manejar_integridad)
    application.add_exception_handler(Exception, manejar_no_controlado)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Total-Count"],
    )
    application.add_middleware(SecurityHeadersMiddleware)
    # Los listados JSON comprimen ~80%: menos transferencia en redes móviles de campo.
    application.add_middleware(GZipMiddleware, minimum_size=1024)

    application.include_router(health.router)
    application.include_router(api_router)

    @application.get("/")
    def raiz() -> dict[str, str]:
        return {
            "servicio": "Consultar Campo – Packing",
            "salud": "/health",
            "docs": "/docs",
            "api": "/api",
        }

    logger.info("Aplicación iniciada (entorno=%s)", settings.APP_ENV)
    return application


app = create_app()
