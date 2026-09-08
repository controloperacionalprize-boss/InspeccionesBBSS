"""Generación y validación de tokens JWT."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.infrastructure.config import settings


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Crea un token de acceso JWT firmado."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica y valida un token de acceso JWT. Lanza jwt.PyJWTError si es inválido."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
