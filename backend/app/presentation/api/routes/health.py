from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_session

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_live() -> dict[str, str]:
    """Liveness: el proceso está vivo, sin consultar dependencias externas."""
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready(session: Session = Depends(get_session)) -> dict[str, str]:
    """Readiness: confirma que la base de datos responde."""
    session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
