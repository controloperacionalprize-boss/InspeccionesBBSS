"""Índice de Inspecciones por subcategoría.

Revision ID: 0004_subcategoria_index
Revises: 0003_roles_and_dni
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0004_subcategoria_index"
down_revision: Union[str, None] = "0003_roles_and_dni"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_inspecciones_subcategoria",
        "Inspecciones",
        ["ID_SUBCATEGORIA"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_inspecciones_subcategoria", table_name="Inspecciones")
