"""CRUD genérico de catálogos sin reglas de negocio propias."""

from typing import Type, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.database.session import get_session
from app.presentation.api.dependencies import get_current_user, require_admin

ModelT = TypeVar("ModelT")
ReadSchemaT = TypeVar("ReadSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)


def crear_router_catalogo(
    *,
    prefix: str,
    tag: str,
    model: Type[ModelT],
    read_schema: Type[ReadSchemaT],
    create_schema: Type[CreateSchemaT],
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("", response_model=list[read_schema])
    def listar(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        session: Session = Depends(get_session),
        _usuario=Depends(get_current_user),
    ) -> list[ModelT]:
        return session.query(model).order_by(model.ID).offset(skip).limit(limit).all()

    @router.get("/{item_id}", response_model=read_schema)
    def obtener(
        item_id: int,
        session: Session = Depends(get_session),
        _usuario=Depends(get_current_user),
    ) -> ModelT:
        item = session.get(model, item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
        return item

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def crear(
        datos: create_schema,
        session: Session = Depends(get_session),
        _usuario=Depends(require_admin),
    ) -> ModelT:
        item = model(**datos.model_dump())
        session.add(item)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(item)
        return item

    @router.put("/{item_id}", response_model=read_schema)
    def actualizar(
        item_id: int,
        datos: create_schema,
        session: Session = Depends(get_session),
        _usuario=Depends(require_admin),
    ) -> ModelT:
        item = session.get(model, item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
        for campo, valor in datos.model_dump().items():
            setattr(item, campo, valor)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        session.refresh(item)
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def eliminar(
        item_id: int,
        session: Session = Depends(get_session),
        _usuario=Depends(require_admin),
    ) -> None:
        item = session.get(model, item_id)
        if item is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
        session.delete(item)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise

    return router
