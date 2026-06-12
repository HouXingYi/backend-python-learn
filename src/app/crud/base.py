from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseCrud(Generic[ModelType]):
    def __init__(self, model: type[ModelType], read_db: Session, write_db: Session):
        self.model = model
        self.read_db = read_db
        self.write_db = write_db

    def insert(self, entity: ModelType, auto_commit: bool = True) -> ModelType:
        self.write_db.add(entity)
        if auto_commit:
            self.write_db.commit()
            self.write_db.refresh(entity)
        else:
            self.write_db.flush()
        return entity

    def update(self, entity: ModelType, auto_commit: bool = True) -> ModelType:
        merged = self.write_db.merge(entity)
        if auto_commit:
            self.write_db.commit()
            self.write_db.refresh(merged)
        else:
            self.write_db.flush()
        return merged

    def delete(self, entity: ModelType, auto_commit: bool = True) -> None:
        if hasattr(entity, "mark_delete"):
            entity.mark_delete()
            self.update(entity, auto_commit=auto_commit)
            return

        merged = self.write_db.merge(entity)
        self.write_db.delete(merged)
        if auto_commit:
            self.write_db.commit()
        else:
            self.write_db.flush()

    def try_select_one(self, conditions: list) -> ModelType | None:
        statement = select(self.model).where(*self._active_conditions(conditions))
        return self.read_db.execute(statement).scalar_one_or_none()

    def select_by_id(self, id: int) -> ModelType | None:
        return self.try_select_one([self.model.id == id])

    def select_list(self, conditions: list, order_by: list | None = None) -> list[ModelType]:
        statement = select(self.model).where(*self._active_conditions(conditions))
        if order_by:
            statement = statement.order_by(*order_by)
        return list(self.read_db.execute(statement).scalars().all())

    def count(self, conditions: list) -> int:
        statement = select(func.count()).select_from(self.model).where(
            *self._active_conditions(conditions)
        )
        return int(self.read_db.execute(statement).scalar_one() or 0)

    def _active_conditions(self, conditions: list) -> list:
        if hasattr(self.model, "is_deleted"):
            return [self.model.is_deleted == 0, *conditions]
        return conditions
