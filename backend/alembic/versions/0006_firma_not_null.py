"""Restaura NOT NULL en Indumentaria.FIRMA (las filas nulas quedan en '').

Revision ID: 0006_firma_not_null
Revises: 0005_firma_nullable
Create Date: 2026-09-11

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006_firma_not_null"
down_revision: Union[str, None] = "0005_firma_nullable"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE \"Indumentaria\" SET \"FIRMA\" = '' WHERE \"FIRMA\" IS NULL")
    op.execute('ALTER TABLE "Indumentaria" ALTER COLUMN "FIRMA" SET NOT NULL')


def downgrade() -> None:
    op.execute('ALTER TABLE "Indumentaria" ALTER COLUMN "FIRMA" DROP NOT NULL')
