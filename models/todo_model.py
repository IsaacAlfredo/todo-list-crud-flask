from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    validates,
)
from models.base_model import db


class Todo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str]
    check: Mapped[bool] = mapped_column(default=False)

    @validates("description", "title")
    def validate_string(self, atribute_key, text):
        if not isinstance(text, str):
            raise TypeError()
        return text

    @validates("check")
    def validate_bool(self, atribute_key, boolean):
        if not isinstance(boolean, bool):
            raise TypeError()
        return boolean
