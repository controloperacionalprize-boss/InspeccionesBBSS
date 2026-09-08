from fastapi import APIRouter

from app.presentation.api.routes import auth, inspecciones, roles, usuarios
from app.presentation.api.routes.catalogos import todos_los_routers_catalogo

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(roles.router)
api_router.include_router(usuarios.router)
api_router.include_router(inspecciones.router)

for _router in todos_los_routers_catalogo:
    api_router.include_router(_router)
