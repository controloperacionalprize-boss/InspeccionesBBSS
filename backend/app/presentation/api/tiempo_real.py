"""Canal WebSocket para que la web refresque listados al instante.

Los endpoints HTTP son síncronos (threadpool): el aviso se encola en el
loop principal con run_coroutine_threadsafe para no bloquear el request.
"""

from __future__ import annotations

import asyncio
import json
import logging

import jwt
from fastapi import WebSocket
from sqlalchemy.orm import Session, joinedload
from starlette.websockets import WebSocketState

from app.infrastructure.database.models import Usuario as UsuarioModel
from app.infrastructure.security.jwt_handler import decode_access_token

logger = logging.getLogger("consultar_campo")


class HubTiempoReal:
    def __init__(self) -> None:
        self._conexiones: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def asignar_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def conectar(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._conexiones.add(websocket)

    def registrar(self, websocket: WebSocket) -> None:
        """La ruta ya aceptó el socket (p. ej. tras autenticar el primer mensaje)."""
        self._conexiones.add(websocket)

    def desconectar(self, websocket: WebSocket) -> None:
        self._conexiones.discard(websocket)

    async def publicar(self, recurso: str) -> None:
        if not self._conexiones:
            return
        mensaje = json.dumps({"recurso": recurso})
        vivos: set[WebSocket] = set()
        for conexion in list(self._conexiones):
            if conexion.client_state != WebSocketState.CONNECTED:
                continue
            try:
                await conexion.send_text(mensaje)
                vivos.add(conexion)
            except Exception:
                logger.debug("WebSocket inactivo, se descarta", exc_info=True)
        self._conexiones = vivos

    async def cerrar_todas(self) -> None:
        for conexion in list(self._conexiones):
            try:
                await conexion.close(code=1001)
            except Exception:
                pass
        self._conexiones.clear()

    def avisar(self, recurso: str) -> None:
        loop = self._loop
        if loop is None or not loop.is_running():
            return
        asyncio.run_coroutine_threadsafe(self.publicar(recurso), loop)


hub = HubTiempoReal()


def avisar(recurso: str) -> None:
    hub.avisar(recurso)


def usuario_desde_token(session: Session, token: str | None) -> bool:
    """True si el JWT es válido y el usuario sigue existiendo."""
    if not token:
        return False

    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        return False
    subject = payload.get("sub")
    uid = payload.get("uid")
    if subject is None or uid is None:
        return False
    modelo = (
        session.query(UsuarioModel)
        .options(joinedload(UsuarioModel.rol))
        .filter(UsuarioModel.USUARIO == subject, UsuarioModel.ID == int(uid))
        .first()
    )
    return modelo is not None
