import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


class DbCheck(db.Model):
    """Single dummy row used to prove the app can write to and read from the DB."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    checks: Mapped[int] = mapped_column(default=0)
    last_checked: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "858fdb4feece1e32a6ed726fc6e3094472458b148c05a4db27"
    )
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

    @app.route("/db-check")
    def db_check():
        try:
            db.create_all()
            row = DbCheck.query.filter_by(name="dummy").first()
            if row is None:
                row = DbCheck(name="dummy", checks=0) # pyright: ignore[reportCallIssue]
                db.session.add(row)
            row.checks += 1
            row.last_checked = datetime.now(UTC)
            db.session.commit()
            return {
                "status": "ok",
                "database": db.engine.dialect.name,
                "checks": row.checks,
                "last_checked": row.last_checked.isoformat(),
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"status": "error", "error": str(e)}, 500

    return app


def main() -> None:
    create_app().run(debug=True)
