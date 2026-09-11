"""Modelos ORM alineados al esquema PostgreSQL."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

def _id_identity() -> Identity:
    # Instancia nueva: Identity no se puede reutilizar entre columnas.
    return Identity(always=True)


class Empresa(Base):
    __tablename__ = "Empresas"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String(30), nullable=False)

    fundos: Mapped[list["Fundo"]] = relationship(back_populates="empresa")


class Division(Base):
    __tablename__ = "Division"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String(100), nullable=False)

    areas: Mapped[list["Area"]] = relationship(back_populates="division")


class Fundo(Base):
    __tablename__ = "Fundo"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_EMPRESA: Mapped[int] = mapped_column(ForeignKey("Empresas.ID"), nullable=False)
    NOMBRE: Mapped[str] = mapped_column(String(50), nullable=False)

    empresa: Mapped["Empresa"] = relationship(back_populates="fundos")


class Area(Base):
    __tablename__ = "Area"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_DIVISION: Mapped[int] = mapped_column(ForeignKey("Division.ID"), nullable=False)
    NOMBRE: Mapped[str] = mapped_column(String(100), nullable=False)

    division: Mapped["Division"] = relationship(back_populates="areas")


class Categoria(Base):
    __tablename__ = "Categoria"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String(150), nullable=False)

    subcategorias: Mapped[list["Subcategoria"]] = relationship(back_populates="categoria")


class Subcategoria(Base):
    __tablename__ = "Subcategoria"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_CATEGORIA: Mapped[int] = mapped_column(ForeignKey("Categoria.ID"), nullable=False)
    NOMBRE: Mapped[str] = mapped_column(String(150), nullable=False)

    categoria: Mapped["Categoria"] = relationship(back_populates="subcategorias")


class Rol(Base):
    __tablename__ = "Roles"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    __tablename__ = "Usuarios"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    NOMBRE: Mapped[str] = mapped_column(String(70), nullable=False)
    APELLIDO: Mapped[str] = mapped_column(String(70), nullable=False)
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
    ACCION_CORRECTIVA: Mapped[str | None] = mapped_column(Text, nullable=True)
    PLAZO_LEVANTAMIENTO: Mapped[str | None] = mapped_column(Text, nullable=True)
    TIPO_CONSULTA: Mapped[str | None] = mapped_column(Text, nullable=True)
    ELIMINADO: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    FECHA_ELIMINACION: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_inspecciones_empresa_fecha", "ID_EMPRESA", "FECHA_OBSERVACION"),
        Index("ix_inspecciones_fundo", "ID_FUNDO"),
        Index("ix_inspecciones_division", "ID_DIVISION"),
        Index("ix_inspecciones_area", "ID_AREA"),
        Index("ix_inspecciones_categoria", "ID_CATEGORIA"),
        Index("ix_inspecciones_subcategoria", "ID_SUBCATEGORIA"),
        Index("ix_inspecciones_fecha", "FECHA_OBSERVACION"),
        Index("ix_inspecciones_eliminado", "ELIMINADO"),
    )


class Consulta(Base):
    __tablename__ = "Consultas"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_EMPRESA: Mapped[int] = mapped_column(ForeignKey("Empresas.ID"), nullable=False)
    ID_FUNDO: Mapped[int] = mapped_column(ForeignKey("Fundo.ID"), nullable=False)
    ID_DIVISION: Mapped[int] = mapped_column(ForeignKey("Division.ID"), nullable=False)
    ID_AREA: Mapped[int] = mapped_column(ForeignKey("Area.ID"), nullable=False)
    FECHA_CONSULTA: Mapped[date] = mapped_column(Date, nullable=False)
    DNI_TRABAJADOR: Mapped[str] = mapped_column(String(20), nullable=False)
    APELLIDOS_NOMBRES: Mapped[str] = mapped_column(String(150), nullable=False)
    DESCRIPCION: Mapped[str] = mapped_column(Text, nullable=False)
    AREA_RESPONSABLE: Mapped[str] = mapped_column(String(150), nullable=False)
    RESPUESTA_INMEDIATA: Mapped[str | None] = mapped_column(Text, nullable=True)
    RESPUESTA_POSTERIOR: Mapped[str | None] = mapped_column(Text, nullable=True)
    TIPO_CONSULTA: Mapped[str | None] = mapped_column(Text, nullable=True)
    ELIMINADO: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    FECHA_ELIMINACION: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_consultas_empresa_fecha", "ID_EMPRESA", "FECHA_CONSULTA"),
        Index("ix_consultas_fundo", "ID_FUNDO"),
        Index("ix_consultas_division", "ID_DIVISION"),
        Index("ix_consultas_area", "ID_AREA"),
        Index("ix_consultas_dni_trabajador", "DNI_TRABAJADOR"),
        Index("ix_consultas_fecha", "FECHA_CONSULTA"),
        Index("ix_consultas_eliminado", "ELIMINADO"),
    )


class Indumentaria(Base):
    __tablename__ = "Indumentaria"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_EMPRESA: Mapped[int] = mapped_column(ForeignKey("Empresas.ID"), nullable=False)
    ID_FUNDO: Mapped[int] = mapped_column(ForeignKey("Fundo.ID"), nullable=False)
    ID_DIVISION: Mapped[int] = mapped_column(ForeignKey("Division.ID"), nullable=False)
    ID_AREA: Mapped[int] = mapped_column(ForeignKey("Area.ID"), nullable=False)
    DNI_TRABAJADOR: Mapped[str] = mapped_column(String(20), nullable=False)
    APELLIDOS_NOMBRES: Mapped[str] = mapped_column(String(150), nullable=False)
    FECHA_ENTREGA: Mapped[date] = mapped_column(Date, nullable=False)
    CANTIDAD: Mapped[int] = mapped_column(Integer, nullable=False)
    TIPO: Mapped[str] = mapped_column(String(100), nullable=False)
    FIRMA: Mapped[str] = mapped_column(Text, nullable=False, default="")
    RESPONSABLE_REGISTRO: Mapped[str] = mapped_column(String(150), nullable=False)
    TIPO_CONSULTA: Mapped[str | None] = mapped_column(Text, nullable=True)
    ELIMINADO: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    FECHA_ELIMINACION: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_indumentaria_empresa_fecha", "ID_EMPRESA", "FECHA_ENTREGA"),
        Index("ix_indumentaria_fundo", "ID_FUNDO"),
        Index("ix_indumentaria_division", "ID_DIVISION"),
        Index("ix_indumentaria_area", "ID_AREA"),
        Index("ix_indumentaria_dni_trabajador", "DNI_TRABAJADOR"),
        Index("ix_indumentaria_fecha_entrega", "FECHA_ENTREGA"),
        Index("ix_indumentaria_eliminado", "ELIMINADO"),
    )


class Foto(Base):
    """Una imagen adjunta a una Inspeccion o a una Consulta (uno a muchos)."""

    __tablename__ = "Fotos"

    ID: Mapped[int] = mapped_column(_id_identity(), primary_key=True)
    ID_INSPECCION: Mapped[int | None] = mapped_column(
        ForeignKey("Inspecciones.ID", ondelete="CASCADE"), nullable=True
    )
    ID_CONSULTA: Mapped[int | None] = mapped_column(
        ForeignKey("Consultas.ID", ondelete="CASCADE"), nullable=True
    )
    OBJECT_KEY: Mapped[str] = mapped_column(Text, nullable=False)
    ORDEN: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    FECHA_SUBIDA: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_fotos_inspeccion", "ID_INSPECCION"),
        Index("ix_fotos_consulta", "ID_CONSULTA"),
    )
