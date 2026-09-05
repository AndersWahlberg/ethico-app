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
        "company_role": None, "is_demo": True, "sources": [],
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
        assert connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 4


def test_real_product_returns_role_and_scoped_sources(client):
    response = client.get("/products/6430051512933")
    assert response.status_code == 200
    product = response.json()
    assert product["product_name"] == "Leader Performance Creatine Monohydrate 300 g"
    assert product["brand"] == "Leader"
    assert product["company"] == "Leader Foods Oy"
    assert product["company_role"] == "manufacturer"
    assert product["is_demo"] is False
    assert len(product["sources"]) == 2
    kespro = next(source for source in product["sources"] if "kespro.com" in source["url"])
    assert "6430051512933" in kespro["supports"]
    assert "manufacturer" in kespro["supports"]
    assert kespro["checked_on"] == "2026-09-05"
    leader = next(source for source in product["sources"] if "leader.fi" in source["url"])
    assert "EAN-to-product match is supported by Kespro" in leader["supports"]


def test_upgrade_preserves_old_rows_and_does_not_duplicate_sources(tmp_path):
    path = tmp_path / "old.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("""CREATE TABLE products (
            ean TEXT PRIMARY KEY, product_name TEXT NOT NULL,
            brand TEXT NOT NULL, company TEXT NOT NULL)""")
        connection.execute("INSERT INTO products VALUES (?, ?, ?, ?)",
                           ("2000000000015", "Edited demo", "Demo Meadow", "Fictional Meadow Foods"))
        connection.execute("INSERT INTO products VALUES (?, ?, ?, ?)",
                           ("2000000000039", "Local product", "Local brand", "Local company"))
    for _ in range(2):
        with TestClient(create_app(path)) as client:
            demo = client.get("/products/2000000000015").json()
            assert demo["product_name"] == "Edited demo"
            assert demo["is_demo"] is True
            assert demo["sources"] == []
            local = client.get("/products/2000000000039").json()
            assert local["product_name"] == "Local product"
            assert local["is_demo"] is False
            assert local["company_role"] is None
            assert local["sources"] == []
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 5
        assert connection.execute("SELECT COUNT(*) FROM product_sources").fetchone()[0] == 2


def test_existing_matching_ean_does_not_get_unreviewed_sources(tmp_path):
    path = tmp_path / "existing.sqlite3"
    with sqlite3.connect(path) as connection:
        connection.execute("""CREATE TABLE products (
            ean TEXT PRIMARY KEY, product_name TEXT NOT NULL,
            brand TEXT NOT NULL, company TEXT NOT NULL)""")
        connection.execute("INSERT INTO products VALUES (?, ?, ?, ?)",
                           ("6430051512933", "Existing name", "Existing brand", "Existing company"))
    with TestClient(create_app(path)) as client:
        product = client.get("/products/6430051512933").json()
        assert product["product_name"] == "Existing name"
        assert product["sources"] == []

