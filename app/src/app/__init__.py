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
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "858fdb4feece1e32a6ed726fc6e3094472458b148c05a4db27")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///dev.db"
    )

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def hello():
        return "Welcome to TasketCasket!"

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


def main() -> None:
    create_app().run(debug=True)
