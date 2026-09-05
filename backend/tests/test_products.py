import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.database import initialize_database
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.sqlite3")) as client:
        yield client


def test_lookup(client):
    response = client.get("/products/2000000000015")
    assert response.status_code == 200
    assert response.json() == {
        "ean": "2000000000015", "product_name": "Demo Oat Drink",
        "brand": "Demo Meadow", "company": "Fictional Meadow Foods",
    }


def test_leading_zeros(client):
    assert client.get("/products/0000000000017").json()["ean"] == "0000000000017"


@pytest.mark.parametrize("ean", ["123", "abcdefgh", "2000000000016", "１２３４５６７８", "' OR 1=1--"])
def test_invalid_ean(client, ean):
    assert client.get(f"/products/{ean}").status_code == 422


@pytest.mark.parametrize("ean", ["2000000000039", "96385074"])
def test_unknown_valid_ean(client, ean):
    assert client.get(f"/products/{ean}").status_code == 404


def test_seed_is_idempotent_and_lookup_reads_database(tmp_path):
    path = tmp_path / "test.sqlite3"
    initialize_database(path)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE products SET product_name = 'Edited demo' WHERE ean = '2000000000015'")
    with TestClient(create_app(path)) as client:
        assert client.get("/products/2000000000015").json()["product_name"] == "Edited demo"
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 3

