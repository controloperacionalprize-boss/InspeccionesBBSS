"""Permite NULL en Indumentaria.FIRMA (aún no se define captura de firma).

Revision ID: 0005_firma_nullable
Revises: 0004_subcategoria_index
Create Date: 2026-09-11

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005_firma_nullable"
down_revision: Union[str, None] = "0004_subcategoria_index"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER TABLE "Indumentaria" ALTER COLUMN "FIRMA" DROP NOT NULL')


def downgrade() -> None:
    # No se restaura NOT NULL: exigiría backfill de firmas inexistentes.
    pass
