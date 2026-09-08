"""Corrige el esquema existente: IDs autoincrementales, NOT NULL en campos
obligatorios, UNIQUE en usuario de login y renombre de columna de contraseña.

Revision ID: 0001_fix_schema_constraints
Revises:
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect as sa_inspect

# revision identifiers, used by Alembic.
revision: str = "0001_fix_schema_constraints"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _crear_esquema_base() -> None:
    """BD vacía: crea el esquema posterior a esta revisión (sin Roles; eso es 0003)."""
    op.execute(
        """
        CREATE TABLE "Empresas" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "NOMBRE" VARCHAR(30) NOT NULL
        );
        CREATE TABLE "Division" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "NOMBRE" VARCHAR(100) NOT NULL
        );
        CREATE TABLE "Fundo" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "ID_EMPRESA" INTEGER NOT NULL REFERENCES "Empresas"("ID"),
            "NOMBRE" VARCHAR(50) NOT NULL
        );
        CREATE TABLE "Area" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "ID_DIVISION" INTEGER NOT NULL REFERENCES "Division"("ID"),
            "NOMBRE" VARCHAR(100) NOT NULL
        );
        CREATE TABLE "Categoria" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "NOMBRE" VARCHAR(150) NOT NULL
        );
        CREATE TABLE "Subcategoria" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "ID_CATEGORIA" INTEGER NOT NULL REFERENCES "Categoria"("ID"),
            "NOMBRE" VARCHAR(150) NOT NULL
        );
        CREATE TABLE "Usuarios" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "NOMBRE" VARCHAR(70) NOT NULL,
            "APELLIDO" VARCHAR(70) NOT NULL,
            "DNI" VARCHAR(20),
            "USUARIO" TEXT NOT NULL,
            "PASSWORD_HASH" TEXT NOT NULL,
            CONSTRAINT uq_usuarios_usuario UNIQUE ("USUARIO")
        );
        CREATE TABLE "Inspecciones" (
            "ID" INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            "ID_EMPRESA" INTEGER NOT NULL REFERENCES "Empresas"("ID"),
            "ID_FUNDO" INTEGER NOT NULL REFERENCES "Fundo"("ID"),
            "ID_DIVISION" INTEGER NOT NULL REFERENCES "Division"("ID"),
            "ID_AREA" INTEGER NOT NULL REFERENCES "Area"("ID"),
            "FECHA_OBSERVACION" DATE NOT NULL,
            "RANGO_HORA" TIMESTAMPTZ,
            "ID_CATEGORIA" INTEGER NOT NULL REFERENCES "Categoria"("ID"),
            "ID_SUBCATEGORIA" INTEGER NOT NULL REFERENCES "Subcategoria"("ID"),
            "DESCRIPCION" TEXT NOT NULL,
            "URL_FOTO" TEXT,
            "ACCION_CORRECTIVA" TEXT,
            "PLAZO_LEVANTAMIENTO" TEXT,
            "TIPO_CONSULTA" TEXT
        );
        """
    )


def upgrade() -> None:
    if not sa_inspect(op.get_bind()).has_table("Empresas"):
        _crear_esquema_base()
        return

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
