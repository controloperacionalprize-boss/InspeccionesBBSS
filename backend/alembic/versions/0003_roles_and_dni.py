"""Tabla Roles (admin, inspector) y FK en Usuarios. DNI pasa a texto.

Revision ID: 0003_roles_and_dni
Revises: 0002_inspecciones_indexes
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003_roles_and_dni"
down_revision: Union[str, None] = "0002_inspecciones_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE "Roles" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "NOMBRE" VARCHAR NOT NULL UNIQUE
        )
        """
    )
    op.execute("INSERT INTO \"Roles\" (\"NOMBRE\") VALUES ('admin'), ('inspector')")

    op.execute('ALTER TABLE "Usuarios" ADD COLUMN "ID_ROL" INTEGER')
    op.execute(
        """
        UPDATE "Usuarios"
        SET "ID_ROL" = (SELECT "ID" FROM "Roles" WHERE "NOMBRE" = 'inspector')
        WHERE "ID_ROL" IS NULL
        """
    )
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "ID_ROL" SET NOT NULL')
    op.execute(
        """
        ALTER TABLE "Usuarios"
        ADD CONSTRAINT id_rol_fk
        FOREIGN KEY ("ID_ROL") REFERENCES "Roles"("ID")
        """
    )

    # DNI es identificador, no una cantidad: numeric provocaba precisión extraña.
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "DNI" TYPE VARCHAR(20) USING "DNI"::text')


def downgrade() -> None:
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "DNI" TYPE NUMERIC USING "DNI"::numeric')
    op.execute('ALTER TABLE "Usuarios" DROP CONSTRAINT IF EXISTS id_rol_fk')
    op.execute('ALTER TABLE "Usuarios" DROP COLUMN "ID_ROL"')
    op.execute('DROP TABLE "Roles"')
