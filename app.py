from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


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


with app.app_context():
    db.create_all()


@app.route("/todo/create", methods=["POST"])
def create():
    new_todo_data = request.json
    todo = Todo(title=new_todo_data["title"], description=new_todo_data["description"])
    db.session.add(todo)
    db.session.commit()
    return {
        "id": todo.id,
        "title": todo.title,
        "description": todo.description,
        "check": todo.check,
    }, 201


@app.route("/todos", methods=["GET"])
def get_todos():
    todos = db.session.execute(db.select(Todo)).scalars()
    return todos.all(), 200
