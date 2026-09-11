"""WebSocket /api/ws — la web se entera de altas/ediciones en campo.

El JWT viaja en el primer mensaje, no en la URL, para no quedar en logs.
"""

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState

from app.infrastructure.database.session import get_session
from app.presentation.api.tiempo_real import hub, usuario_desde_token

router = APIRouter(tags=["Tiempo real"])


async def _cerrar(websocket: WebSocket, code: int) -> None:
    if websocket.client_state != WebSocketState.CONNECTED:
        return
    try:
        await websocket.close(code=code)
    except Exception:
        pass


@router.websocket("/ws")
async def tiempo_real(
    websocket: WebSocket,
    session: Session = Depends(get_session),
) -> None:
    await websocket.accept()
    try:
        token = await asyncio.wait_for(websocket.receive_text(), timeout=10)
    except (TimeoutError, WebSocketDisconnect, Exception):
        await _cerrar(websocket, 4401)
        return
    if not usuario_desde_token(session, token):
        await _cerrar(websocket, 4401)
        return

    hub.registrar(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        hub.desconectar(websocket)
