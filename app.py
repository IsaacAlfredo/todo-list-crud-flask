from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    validates,
)


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todoinfo.db"
db.init_app(app)


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


with app.app_context():
    db.create_all()


@app.route("/todo", methods=["POST"])
def create():
    new_todo_data = request.json
    try:
        if not db.session.execute(
            db.select(Todo).filter_by(title=request.json["title"])
        ).scalar_one_or_none():
            new_todo = Todo(
                title=new_todo_data["title"], description=new_todo_data["description"]
            )
            db.session.add(new_todo)

            db.session.commit()
            return (
                {
                    "id": new_todo.id,
                    "title": new_todo.title,
                    "description": new_todo.description,
                    "check": new_todo.check,
                },
                201,
                {"Location": f"/todo/{new_todo.id}"},
            )
        return (
            "",
            409,
            {
                "Message": "Todo title already exists",
                "Title-Conflicted": request.json["title"],
            },
        )
    except KeyError:
        return {
            "error": "Bad Request",
            "message": "Title field is required.",
        }, 400
    except TypeError:
        return {
            "error": "Bad Request",
            "message": "Title and description fields must be String type.",
        }, 400


@app.route("/todo/<id>", methods=["GET"])
def get_todo(id):
    todo = db.session.execute(db.select(Todo).filter_by(id=id)).scalar_one_or_none()
    if not todo:
        return "", 404
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "check": todo.check,
    }, 200


@app.route("/todo/<id>", methods=["DELETE"])
def delete_todo(id):
    deleted_todo = db.session.execute(
        db.select(Todo).filter_by(id=id)
    ).scalar_one_or_none()
    if not deleted_todo:
        return "", 404
    db.session.delete(deleted_todo)
    db.session.commit()
    return "", 204


@app.route("/todo/<id>", methods=["PATCH"])
def update_todo(id):
    updated_todo = db.session.execute(
        db.select(Todo).filter_by(id=id)
    ).scalar_one_or_none()
    if not updated_todo:
        return "", 404
    try:
        if "check" in request.json:
            updated_todo.check = request.json["check"]
        if "title" in request.json:
            updated_todo.title = request.json["title"]
        if "description" in request.json:
            updated_todo.description = request.json["description"]

        db.session.commit()
        return "", 204
    except KeyError:
        return {
            "error": "Bad Request",
            "message": "Title field is required.",
        }, 400
    except TypeError:
        return {
            "error": "Bad Request",
            "message": "Unexpected type recieved in body request.",
        }, 400


@app.route("/todo", methods=["GET"])
def get_todos():
    todos = db.session.execute(db.select(Todo)).scalars()
    return todos.all(), 200
