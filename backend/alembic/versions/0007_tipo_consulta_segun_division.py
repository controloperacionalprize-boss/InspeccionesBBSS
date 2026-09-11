"""Alinea TIPO_CONSULTA con el nombre de la división.

Packing si el nombre contiene 'packing'; Campo en cualquier otro caso.

Revision ID: 0007_tipo_segun_division
Revises: 0006_firma_not_null
Create Date: 2026-09-11

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0007_tipo_segun_division"
down_revision: Union[str, None] = "0006_firma_not_null"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SQL = """
UPDATE "{tabla}" t
SET "TIPO_CONSULTA" = CASE
  WHEN lower(d."NOMBRE") LIKE '%packing%' THEN 'Packing'
  ELSE 'Campo'
END
FROM "Division" d
WHERE t."ID_DIVISION" = d."ID"
"""


def upgrade() -> None:
    for tabla in ("Inspecciones", "Consultas", "Indumentaria"):
        op.execute(_SQL.format(tabla=tabla))


def downgrade() -> None:
    pass
