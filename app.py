from flask import Flask, request
from models.base_model import db
from models.todo_model import Todo
from flask_cors import CORS
from os import getenv
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todoinfo.db"
CORS(app, origins=getenv("CLIENT_URL"))
db.init_app(app)


with app.app_context():
    db.create_all()


@app.route("/", methods=["POST"])
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
                {"Location": f"/{new_todo.id}"},
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
            "message": "Title and description fields are required.",
        }, 400
    except TypeError:
        return {
            "error": "Bad Request",
            "message": "Title and description fields must be String type.",
        }, 400


@app.route("/<id>", methods=["GET"])
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


@app.route("/<id>", methods=["DELETE"])
def delete_todo(id):
    deleted_todo = db.session.execute(
        db.select(Todo).filter_by(id=id)
    ).scalar_one_or_none()
    if not deleted_todo:
        return "", 404
    db.session.delete(deleted_todo)
    db.session.commit()
    return "", 204


@app.route("/<id>", methods=["PATCH"])
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
            if not updated_todo.title == request.json["title"]:
                title_exists = db.session.execute(
                    db.select(Todo).filter_by(title=request.json["title"])
                ).scalar_one_or_none()
                if not title_exists:
                    updated_todo.title = request.json["title"]
                else:
                    return (
                        "",
                        409,
                        {
                            "Message": "Todo title already exists in another Todo",
                            "Title-Conflicted": request.json["title"],
                        },
                    )

        if "description" in request.json:
            updated_todo.description = request.json["description"]

        db.session.commit()
        return "", 204

    except TypeError:
        return {
            "error": "Bad Request",
            "message": "Unexpected type received in body request.",
        }, 400


@app.route("/", methods=["GET", "OPTIONS"])
def get_todos():
    todos = db.session.execute(db.select(Todo)).scalars()
    return todos.all(), 200


if __name__ == "__main__":
    app.run(debug=True)
