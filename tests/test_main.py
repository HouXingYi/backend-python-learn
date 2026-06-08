from app.main import greet


def test_greet_default_name() -> None:
    assert greet() == "Hello, Python!"


def test_greet_custom_name() -> None:
    assert greet("JS developer") == "Hello, JS developer!"
