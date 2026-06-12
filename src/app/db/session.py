from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _pool_options(database_url: str) -> dict[str, object]:
    if database_url in {"sqlite://", "sqlite:///:memory:"}:
        return {"poolclass": StaticPool}
    return {}


settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args=_connect_args(settings.database_url),
    pool_pre_ping=True,
    **_pool_options(settings.database_url),
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    yield from _session_scope()


def get_read_db() -> Generator[Session, None, None]:
    yield from _session_scope()


def get_write_db() -> Generator[Session, None, None]:
    yield from _session_scope()


def _session_scope() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables() -> None:
    from app.models import product  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_product_schema()


def _ensure_product_schema() -> None:
    with engine.begin() as connection:
        inspector = inspect(connection)
        if not inspector.has_table("products"):
            return

        columns = {column["name"] for column in inspector.get_columns("products")}
        if "is_deleted" not in columns:
            connection.execute(
                text("ALTER TABLE products ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0")
            )
