"""Modelos ORM alineados al esquema PostgreSQL."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Identity, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

def _id_identity() -> Identity:
    # Instancia nueva: Identity no se puede reutilizar entre columnas.
    return Identity(always=True)


class Empresa(Base):
    __tablename__ = "Empresas"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)

    fundos: Mapped[list["Fundo"]] = relationship(back_populates="empresa")


class Division(Base):
    __tablename__ = "Division"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)

    areas: Mapped[list["Area"]] = relationship(back_populates="division")


class Fundo(Base):
    __tablename__ = "Fundo"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_EMPRESA: Mapped[int] = mapped_column(ForeignKey("Empresas.ID"), nullable=False)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)

    empresa: Mapped["Empresa"] = relationship(back_populates="fundos")


class Area(Base):
    __tablename__ = "Area"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_DIVISION: Mapped[int] = mapped_column(ForeignKey("Division.ID"), nullable=False)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)

    division: Mapped["Division"] = relationship(back_populates="areas")


class Categoria(Base):
    __tablename__ = "Categoria"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)

    subcategorias: Mapped[list["Subcategoria"]] = relationship(back_populates="categoria")


class Subcategoria(Base):
    __tablename__ = "Subcategoria"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_CATEGORIA: Mapped[int] = mapped_column(ForeignKey("Categoria.ID"), nullable=False)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)

    categoria: Mapped["Categoria"] = relationship(back_populates="subcategorias")


class Rol(Base):
    __tablename__ = "Roles"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    __tablename__ = "Usuarios"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String, nullable=False)
    APELLIDO: Mapped[str] = mapped_column(String, nullable=False)
    DNI: Mapped[str | None] = mapped_column(String(20), nullable=True)
    USUARIO: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    PASSWORD_HASH: Mapped[str] = mapped_column(Text, nullable=False)
    ID_ROL: Mapped[int] = mapped_column(ForeignKey("Roles.ID"), nullable=False)

    rol: Mapped["Rol"] = relationship(back_populates="usuarios")


class Inspeccion(Base):
    __tablename__ = "Inspecciones"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_EMPRESA: Mapped[int] = mapped_column(ForeignKey("Empresas.ID"), nullable=False)
    ID_FUNDO: Mapped[int] = mapped_column(ForeignKey("Fundo.ID"), nullable=False)
    ID_DIVISION: Mapped[int] = mapped_column(ForeignKey("Division.ID"), nullable=False)
    ID_AREA: Mapped[int] = mapped_column(ForeignKey("Area.ID"), nullable=False)
    FECHA_OBSERVACION: Mapped[date] = mapped_column(Date, nullable=False)
    RANGO_HORA: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ID_CATEGORIA: Mapped[int] = mapped_column(ForeignKey("Categoria.ID"), nullable=False)
    ID_SUBCATEGORIA: Mapped[int] = mapped_column(ForeignKey("Subcategoria.ID"), nullable=False)
    DESCRIPCION: Mapped[str] = mapped_column(Text, nullable=False)
    URL_FOTO: Mapped[str | None] = mapped_column(Text, nullable=True)
    ACCION_CORRECTIVA: Mapped[str | None] = mapped_column(Text, nullable=True)
    PLAZO_LEVANTAMIENTO: Mapped[str | None] = mapped_column(Text, nullable=True)
    TIPO_CONSULTA: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_inspecciones_empresa_fecha", "ID_EMPRESA", "FECHA_OBSERVACION"),
        Index("ix_inspecciones_fundo", "ID_FUNDO"),
        Index("ix_inspecciones_division", "ID_DIVISION"),
        Index("ix_inspecciones_area", "ID_AREA"),
        Index("ix_inspecciones_categoria", "ID_CATEGORIA"),
        Index("ix_inspecciones_fecha", "FECHA_OBSERVACION"),
    )
