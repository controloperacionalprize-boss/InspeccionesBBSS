from fastapi import HTTPException

from app.domain.entities import Usuario
from app.domain.roles import ROL_ADMIN, ROL_INSPECTOR
from app.presentation.api.dependencies import require_admin


def test_require_admin_acepta_admin():
    usuario = Usuario(id=1, nombre="A", apellido="B", usuario="jefe", rol=ROL_ADMIN)
    assert require_admin(usuario) == usuario


def test_require_admin_rechaza_inspector():
    usuario = Usuario(id=2, nombre="A", apellido="B", usuario="insp", rol=ROL_INSPECTOR)
    try:
        require_admin(usuario)
        raise AssertionError("debía rechazar inspector")
    except HTTPException as exc:
        assert exc.status_code == 403
