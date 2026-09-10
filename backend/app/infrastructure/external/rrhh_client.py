"""Consulta de solo lectura al maestro de personal (RDS, base separada de RRHH).

La tabla `qbiz_funcionarios_raw` guarda un payload JSON por sincronización;
un mismo DNI puede tener varias filas (historial). Se prioriza el registro
vigente (VIGENCIA='SI') y, entre esos, el más reciente por FECHA_MODIF.
"""

from dataclasses import dataclass
from functools import lru_cache

from sqlalchemy import create_engine, text

from app.infrastructure.config import settings


class RrhhNoConfiguradoError(RuntimeError):
    """El entorno no tiene configurada AWS_DATABASE_URL."""


@dataclass(frozen=True)
class Trabajador:
    dni: str
    apellidos_nombres: str
    empresa: str | None
    cargo: str | None
    vigente: bool


@lru_cache(maxsize=1)
def _engine():
    if not settings.AWS_DATABASE_URL:
        raise RrhhNoConfiguradoError("Falta AWS_DATABASE_URL en el entorno.")
    return create_engine(
        settings.AWS_DATABASE_URL,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=True,
        pool_recycle=300,
    )


_CONSULTA = text(
    """
    SELECT
        payload->>'DNI' AS dni,
        payload->>'NOMBRES' AS nombres,
        payload->>'APELLIDO PATERNO' AS apellido_paterno,
        payload->>'APELLIDO MATERNO' AS apellido_materno,
        payload->>'EMPRESA' AS empresa,
        payload->>'CARGO' AS cargo,
        payload->>'VIGENCIA' AS vigencia
    FROM qbiz_funcionarios_raw
    WHERE payload->>'DNI' = :dni
    ORDER BY (payload->>'VIGENCIA') DESC, fecha_modif DESC
    LIMIT 1
    """
)


def buscar_trabajador_por_dni(dni: str) -> Trabajador | None:
    with _engine().connect() as conn:
        fila = conn.execute(_CONSULTA, {"dni": dni}).mappings().first()

    if fila is None:
        return None

    partes_nombre = [
        (fila["apellido_paterno"] or "").strip(),
        (fila["apellido_materno"] or "").strip(),
        (fila["nombres"] or "").strip(),
    ]
    apellidos_nombres = " ".join(parte for parte in partes_nombre if parte)

    return Trabajador(
        dni=fila["dni"],
        apellidos_nombres=apellidos_nombres,
        empresa=fila["empresa"],
        cargo=fila["cargo"],
        vigente=(fila["vigencia"] or "").upper() == "SI",
    )
