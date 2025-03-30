from flask import Flask
from models.base_model import db
from routes.todo_routes import todo_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todoinfo.db"
app.register_blueprint(todo_bp)

db.init_app(app)

with app.app_context():
    db.create_all()
