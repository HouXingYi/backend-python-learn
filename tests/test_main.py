import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["AGENT_MODE"] = "mock"

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError

import app.main as main_module
from app.crud import products as products_crud
from app.db.session import Base, engine
from app.main import DATABASE_UNAVAILABLE_MESSAGE, app, greet


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_greet_default_name() -> None:
    assert greet() == "Hello, Python!"


def test_greet_custom_name() -> None:
    assert greet("JS developer") == "Hello, JS developer!"


def test_read_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}


def test_product_crud_flow() -> None:
    create_response = client.post(
        "/api/products",
        json={
            "name": "FastAPI 手册",
            "description": "学习 CRUD",
            "price": 99.9,
            "stock": 10,
        },
    )
    assert create_response.status_code == 201
    product = create_response.json()
    assert product["name"] == "FastAPI 手册"
    assert product["stock"] == 10

    list_response = client.get("/api/products")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.put(
        f"/api/products/{product['id']}",
        json={"stock": 8},
    )
    assert update_response.status_code == 200
    assert update_response.json()["stock"] == 8

    delete_response = client.delete(f"/api/products/{product['id']}")
    assert delete_response.status_code == 204

    empty_response = client.get("/api/products")
    assert empty_response.status_code == 200
    assert empty_response.json() == []


def test_database_error_returns_service_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_database_error(*_: object, **__: object) -> None:
        raise OperationalError("SELECT 1", {}, ConnectionRefusedError("refused"))

    monkeypatch.setattr(products_crud, "list_products", raise_database_error)

    response = client.get("/api/products")

    assert response.status_code == 503
    assert response.json() == {"detail": DATABASE_UNAVAILABLE_MESSAGE}


def test_startup_database_error_does_not_stop_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_database_error() -> None:
        raise OperationalError("CREATE TABLE", {}, ConnectionRefusedError("refused"))

    monkeypatch.setattr(main_module, "create_db_and_tables", raise_database_error)

    with TestClient(app) as startup_client:
        response = startup_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}


def test_agent_chat_stream_mock() -> None:
    with client.stream(
        "POST",
        "/api/agent/chat/stream",
        json={"messages": [{"role": "user", "content": "你好"}]},
    ) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert "event: message" in body
    assert "event: done" in body
