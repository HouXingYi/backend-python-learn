from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.core.config import get_settings
from app.db.session import create_db_and_tables
from app.routers import agent, products


settings = get_settings()
logger = logging.getLogger(__name__)
DATABASE_UNAVAILABLE_MESSAGE = (
    "数据库暂时不可用，请确认 MySQL 已启动：docker compose up -d mysql"
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    if settings.auto_create_tables:
        try:
            create_db_and_tables()
        except OperationalError as exc:
            log_database_unavailable(exc)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(OperationalError)
async def handle_database_error(
    _: Request,
    exc: OperationalError,
) -> JSONResponse:
    log_database_unavailable(exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": DATABASE_UNAVAILABLE_MESSAGE},
    )


def log_database_unavailable(exc: OperationalError) -> None:
    logger.warning("Database is unavailable: %s", exc.orig)


def greet(name: str = "Python") -> str:
    return f"Hello, {name}!"


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": greet("FastAPI")}


app.include_router(products.router)
app.include_router(agent.router)


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
