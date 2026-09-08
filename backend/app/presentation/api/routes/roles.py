from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Rol
from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user
from app.presentation.api.schemas.catalogos import RolRead

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RolRead])
def listar(
    session: Session = Depends(get_session),
    _usuario=Depends(get_current_user),
) -> list[Rol]:
    return session.query(Rol).order_by(Rol.ID).all()
