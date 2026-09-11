from fastapi import APIRouter

from app.presentation.api.routes import (
    auth,
    consolidados,
    consultas,
    fotos,
    indumentaria,
    inspecciones,
    roles,
    trabajadores,
    usuarios,
    tiempo_real,
)
from app.presentation.api.routes.catalogos import todos_los_routers_catalogo

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(roles.router)
api_router.include_router(usuarios.router)
api_router.include_router(inspecciones.router)
api_router.include_router(fotos.router)
api_router.include_router(trabajadores.router)
api_router.include_router(consultas.router)
api_router.include_router(indumentaria.router)
api_router.include_router(consolidados.router)
api_router.include_router(tiempo_real.router)

for _router in todos_los_routers_catalogo:
    api_router.include_router(_router)
