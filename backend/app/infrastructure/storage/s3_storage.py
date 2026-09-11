"""Cliente de object storage S3-compatible (p.ej. Neon Object Storage)."""

import time
from functools import lru_cache
from threading import Lock

import boto3
from botocore.client import Config as BotoConfig

from app.infrastructure.config import settings

_VIGENCIA_URL = 3600
# Se reutiliza la misma URL mientras le queden al menos 10 min: si cambiara en cada
# petición (la firma incluye la hora), el navegador no podría cachear la imagen.
_MARGEN_REUSO = 600
_urls: dict[str, tuple[str, float]] = {}
_candado = Lock()


class StorageNoConfiguradoError(RuntimeError):
    """El entorno no tiene configuradas las variables S3_*."""


@lru_cache(maxsize=1)
def _cliente():
    if not (
        settings.AWS_ENDPOINT_URL_S3
        and settings.S3_BUCKET_NAME
        and settings.AWS_ACCESS_KEY_ID
        and settings.AWS_SECRET_ACCESS_KEY
    ):
        raise StorageNoConfiguradoError(
            "Faltan variables AWS_ENDPOINT_URL_S3/S3_BUCKET_NAME/AWS_ACCESS_KEY_ID/"
            "AWS_SECRET_ACCESS_KEY en el entorno."
        )
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_ENDPOINT_URL_S3,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=BotoConfig(signature_version="s3v4"),
    )


def subir_objeto(clave: str, contenido: bytes, content_type: str) -> None:
    _cliente().put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=clave,
        Body=contenido,
        ContentType=content_type,
        # La clave lleva un uuid: el contenido de una clave nunca cambia.
        CacheControl="private, max-age=31536000, immutable",
    )


def eliminar_objeto(clave: str) -> None:
    _cliente().delete_object(Bucket=settings.S3_BUCKET_NAME, Key=clave)
    with _candado:
        _urls.pop(clave, None)


def url_firmada(clave: str) -> str:
    ahora = time.time()
    with _candado:
        guardada = _urls.get(clave)
        if guardada and guardada[1] - ahora > _MARGEN_REUSO:
            return guardada[0]
    url = _cliente().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": clave},
        ExpiresIn=_VIGENCIA_URL,
    )
    with _candado:
        if len(_urls) > 5000:
            for vencida in [k for k, (_, expira) in _urls.items() if expira <= ahora]:
                del _urls[vencida]
        _urls[clave] = (url, ahora + _VIGENCIA_URL)
    return url
