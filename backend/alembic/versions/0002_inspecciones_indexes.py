"""Índices para las consultas de Inspecciones (filtros por empresa, fundo y fecha).

Revision ID: 0002_inspecciones_indexes
Revises: 0001_fix_schema_constraints
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_inspecciones_indexes"
down_revision: Union[str, None] = "0001_fix_schema_constraints"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_inspecciones_empresa_fecha",
        "Inspecciones",
        ["ID_EMPRESA", "FECHA_OBSERVACION"],
    )
    op.create_index("ix_inspecciones_fundo", "Inspecciones", ["ID_FUNDO"])
    op.create_index("ix_inspecciones_division", "Inspecciones", ["ID_DIVISION"])
    op.create_index("ix_inspecciones_area", "Inspecciones", ["ID_AREA"])
    op.create_index("ix_inspecciones_categoria", "Inspecciones", ["ID_CATEGORIA"])
    op.create_index("ix_inspecciones_fecha", "Inspecciones", ["FECHA_OBSERVACION"])


def downgrade() -> None:
    op.drop_index("ix_inspecciones_fecha", table_name="Inspecciones")
    op.drop_index("ix_inspecciones_categoria", table_name="Inspecciones")
    op.drop_index("ix_inspecciones_area", table_name="Inspecciones")
    op.drop_index("ix_inspecciones_division", table_name="Inspecciones")
    op.drop_index("ix_inspecciones_fundo", table_name="Inspecciones")
    op.drop_index("ix_inspecciones_empresa_fecha", table_name="Inspecciones")
