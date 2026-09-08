"""Corrige el esquema existente: IDs autoincrementales, NOT NULL en campos
obligatorios, UNIQUE en usuario de login y renombre de columna de contraseña.

Revision ID: 0001_fix_schema_constraints
Revises:
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_fix_schema_constraints"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Nota: los "ID" ya son columnas IDENTITY (attidentity) en todas las tablas;
    # no se requiere ninguna acción adicional para el autoincremento.

    # 1. Renombrar columna de contraseña (evita problemas de encoding con la Ñ)
    op.execute('ALTER TABLE "Usuarios" RENAME COLUMN "CONTRASE\u00d1A" TO "PASSWORD_HASH"')

    # 2. NOT NULL en columnas obligatorias de negocio
    op.execute('ALTER TABLE "Empresas" ALTER COLUMN "NOMBRE" SET NOT NULL')
    op.execute('ALTER TABLE "Division" ALTER COLUMN "NOMBRE" SET NOT NULL')

    op.execute('ALTER TABLE "Fundo" ALTER COLUMN "NOMBRE" SET NOT NULL')
    op.execute('ALTER TABLE "Fundo" ALTER COLUMN "ID_EMPRESA" SET NOT NULL')

    op.execute('ALTER TABLE "Area" ALTER COLUMN "NOMBRE" SET NOT NULL')
    op.execute('ALTER TABLE "Area" ALTER COLUMN "ID_DIVISION" SET NOT NULL')

    op.execute('ALTER TABLE "Categoria" ALTER COLUMN "NOMBRE" SET NOT NULL')

    op.execute('ALTER TABLE "Subcategoria" ALTER COLUMN "NOMBRE" SET NOT NULL')
    op.execute('ALTER TABLE "Subcategoria" ALTER COLUMN "ID_CATEGORIA" SET NOT NULL')

    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "NOMBRE" SET NOT NULL')
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "APELLIDO" SET NOT NULL')
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "USUARIO" SET NOT NULL')
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "PASSWORD_HASH" SET NOT NULL')

    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_EMPRESA" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_FUNDO" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_DIVISION" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_AREA" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "FECHA_OBSERVACION" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_CATEGORIA" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_SUBCATEGORIA" SET NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "DESCRIPCION" SET NOT NULL')

    # 3. UNIQUE en el usuario de login
    op.execute(
        'ALTER TABLE "Usuarios" ADD CONSTRAINT uq_usuarios_usuario UNIQUE ("USUARIO")'
    )


def downgrade() -> None:
    op.execute('ALTER TABLE "Usuarios" DROP CONSTRAINT IF EXISTS uq_usuarios_usuario')

    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "DESCRIPCION" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_SUBCATEGORIA" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_CATEGORIA" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "FECHA_OBSERVACION" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_AREA" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_DIVISION" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_FUNDO" DROP NOT NULL')
    op.execute('ALTER TABLE "Inspecciones" ALTER COLUMN "ID_EMPRESA" DROP NOT NULL')

    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "PASSWORD_HASH" DROP NOT NULL')
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "USUARIO" DROP NOT NULL')
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "APELLIDO" DROP NOT NULL')
    op.execute('ALTER TABLE "Usuarios" ALTER COLUMN "NOMBRE" DROP NOT NULL')

    op.execute('ALTER TABLE "Subcategoria" ALTER COLUMN "ID_CATEGORIA" DROP NOT NULL')
    op.execute('ALTER TABLE "Subcategoria" ALTER COLUMN "NOMBRE" DROP NOT NULL')

    op.execute('ALTER TABLE "Categoria" ALTER COLUMN "NOMBRE" DROP NOT NULL')

    op.execute('ALTER TABLE "Area" ALTER COLUMN "ID_DIVISION" DROP NOT NULL')
    op.execute('ALTER TABLE "Area" ALTER COLUMN "NOMBRE" DROP NOT NULL')

    op.execute('ALTER TABLE "Fundo" ALTER COLUMN "ID_EMPRESA" DROP NOT NULL')
    op.execute('ALTER TABLE "Fundo" ALTER COLUMN "NOMBRE" DROP NOT NULL')

    op.execute('ALTER TABLE "Division" ALTER COLUMN "NOMBRE" DROP NOT NULL')
    op.execute('ALTER TABLE "Empresas" ALTER COLUMN "NOMBRE" DROP NOT NULL')

    op.execute('ALTER TABLE "Usuarios" RENAME COLUMN "PASSWORD_HASH" TO "CONTRASE\u00d1A"')
