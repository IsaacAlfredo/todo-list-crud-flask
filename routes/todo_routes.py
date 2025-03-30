from models.todo_model import Todo
from flask import request, Blueprint
from models.base_model import db

todo_bp = Blueprint("routes", __name__, url_prefix="/todo")


@todo_bp.route("/", methods=["POST"])
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


@todo_bp.route("/<id>", methods=["GET"])
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


@todo_bp.route("/<id>", methods=["DELETE"])
def delete_todo(id):
    deleted_todo = db.session.execute(
        db.select(Todo).filter_by(id=id)
    ).scalar_one_or_none()
    if not deleted_todo:
        return "", 404
    db.session.delete(deleted_todo)
    db.session.commit()
    return "", 204


@todo_bp.route("/<id>", methods=["PATCH"])
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


@todo_bp.route("/", methods=["GET"])
def get_todos():
    todos = db.session.execute(db.select(Todo)).scalars()
    return todos.all(), 200
