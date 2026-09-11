"""Endpoint para subir fotos de inspecciones."""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse

from app.domain.entities import Usuario
from app.presentation.api.dependencies import get_current_user

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("")
async def subir_foto(
    file: UploadFile,
    _usuario: Usuario = Depends(get_current_user),
) -> dict:
    ext = os.path.splitext(file.filename or "foto.jpg")[1] or ".jpg"
    nombre = f"{uuid.uuid4().hex}{ext}"
    ruta = UPLOAD_DIR / nombre

    contenido = await file.read()
    ruta.write_bytes(contenido)

    return {"url": f"/api/uploads/{nombre}", "filename": nombre}


@router.get("/{filename}")
async def obtener_foto(filename: str) -> FileResponse:
    ruta = UPLOAD_DIR / filename
    return FileResponse(ruta)
