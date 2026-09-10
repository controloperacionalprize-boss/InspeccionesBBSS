"""Cliente de object storage S3-compatible (p.ej. Neon Object Storage)."""

from functools import lru_cache

import boto3
from botocore.client import Config as BotoConfig

from app.infrastructure.config import settings


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
    )


def eliminar_objeto(clave: str) -> None:
    _cliente().delete_object(Bucket=settings.S3_BUCKET_NAME, Key=clave)


def url_firmada(clave: str, expira_segundos: int = 3600) -> str:
    return _cliente().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": clave},
        ExpiresIn=expira_segundos,
    )
