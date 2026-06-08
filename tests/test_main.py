from fastapi.testclient import TestClient

from app.main import app, greet


client = TestClient(app)


def test_greet_default_name() -> None:
    assert greet() == "Hello, Python!"


def test_greet_custom_name() -> None:
    assert greet("JS developer") == "Hello, JS developer!"


def test_read_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello, FastAPI!"}
