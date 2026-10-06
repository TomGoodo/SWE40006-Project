import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///dev.db"
    )

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def hello():
        return "Hello, Docker!"

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


def main() -> None:
    create_app().run(debug=True)
