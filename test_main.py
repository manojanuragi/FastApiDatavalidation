from fastapi.testclient import TestClient
from main import app
client = TestClient(app)

VALID = {
    "title": "clean code",
    "author": "Robert Martin",
    "isbn": "9780132350884",
    "price": 29.99,
    "year": 2008,
}
def test_pydantic_accepts_valid_book():
    r = client.post("/pydantic/books", json=VALID)
    assert r.status_code == 201
    assert r.json()["title"] == "Clean Code"  # field_validator ran

def test_pydantic_converts_string_price():
    r = client.post("/pydantic/books", json={**VALID, "price": "29.99"})
    assert r.status_code == 201
    assert r.json()["price_type"] == "float"

def test_dataclass_keeps_string_price():
    r = client.post("/dataclass/books", json={**VALID, "price": "29.99"})
    assert r.status_code == 200
    assert r.json()["price_type"] == "str"  # no conversion, no error
def test_strict_mode_rejects_string_price():
    r = client.post("/pydantic-strict/books", json={**VALID, "price": "29.99"})
    assert r.status_code == 422

def test_pydantic_rejects_negative_price():
    r = client.post("/pydantic/books", json={**VALID, "price": -5})
    assert r.status_code == 422


def test_dataclass_accepts_negative_price():
    r = client.post("/dataclass/books", json={**VALID, "price": -5})
    assert r.status_code == 200  # no check written for price


def test_dataclass_post_init_rejects_short_isbn():
    r = client.post("/dataclass/books", json={**VALID, "isbn": "123"})
    assert r.status_code == 422
def test_pydantic_dataclass_validates_year():
    r = client.post("/pydantic-dataclass/books", json={**VALID, "year": -100})
    assert r.status_code == 422

def test_frozen_model_cannot_change():
    r = client.post("/frozen-demo", json=VALID)
    assert r.json() == {"changed": False, "error": "frozen_instance"}
def test_compare_shows_differences():
    r = client.post("/compare", json={**VALID, "price": "29.99"})
    body = r.json()
    assert body["dataclass"]["price_type"] == "str"
    assert body["pydantic"]["price_type"] == "float"
    assert body["pydantic_strict"]["accepted"] is False
    assert body["pydantic_dataclass"]["price_type"] == "float"