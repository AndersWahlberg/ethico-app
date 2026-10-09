import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from app.database import initialize_database
from app.validate_curated import (
    CURATED_PRODUCTS_PATH,
    CuratedDataError,
    load_curated_products,
    validate_dataset,
)


@pytest.fixture
def dataset():
    return json.loads(CURATED_PRODUCTS_PATH.read_text(encoding="utf-8"))


def assert_rejected_before_database(tmp_path, dataset, field):
    curated = tmp_path / "curated.json"
    curated.write_text(json.dumps(dataset), encoding="utf-8")
    database = tmp_path / "untouched.sqlite3"
    with pytest.raises(CuratedDataError) as caught:
        initialize_database(database, curated)
    assert field in str(caught.value)
    assert str(curated) in str(caught.value)
    assert not database.exists()


def test_current_dataset_passes_without_modification(dataset):
    original = copy.deepcopy(dataset)
    assert validate_dataset(dataset) is dataset
    assert dataset == original
    assert load_curated_products() == dataset


@pytest.mark.parametrize("ean", [
    12345678, None, True, "123", "abcdefgh", "１２３４５６７８", "2000000000016",
])
def test_invalid_ean_rejected_before_import(tmp_path, dataset, ean):
    dataset[0]["ean"] = ean
    assert_rejected_before_database(tmp_path, dataset, "products[0].ean")


def test_duplicate_ean_rejected(tmp_path, dataset):
    dataset.append(copy.deepcopy(dataset[0]))
    assert_rejected_before_database(tmp_path, dataset, "products[1].ean: duplicate EAN")


@pytest.mark.parametrize("field", [
    "ean", "product_name", "brand", "company", "company_role", "sources",
])
def test_missing_product_fields(tmp_path, dataset, field):
    del dataset[0][field]
    assert_rejected_before_database(tmp_path, dataset, f".{field}")


@pytest.mark.parametrize("field", ["product_name", "brand", "company", "company_role"])
@pytest.mark.parametrize("value", ["", " \t\n", 42, False, []])
def test_invalid_product_text(tmp_path, dataset, field, value):
    dataset[0][field] = value
    assert_rejected_before_database(tmp_path, dataset, f".{field}")


@pytest.mark.parametrize("field", ["product_name", "brand", "company"])
def test_null_required_product_text(tmp_path, dataset, field):
    dataset[0][field] = None
    assert_rejected_before_database(tmp_path, dataset, f".{field}")


@pytest.mark.parametrize("value", [None, {}, "sources"])
def test_sources_must_be_list(tmp_path, dataset, value):
    dataset[0]["sources"] = value
    assert_rejected_before_database(tmp_path, dataset, ".sources")


@pytest.mark.parametrize("value", [None, [], "source", 1])
def test_source_must_be_object(tmp_path, dataset, value):
    dataset[0]["sources"] = [value]
    assert_rejected_before_database(tmp_path, dataset, ".sources[0]")


@pytest.mark.parametrize("field", ["title", "url", "checked_on", "supports"])
def test_missing_source_fields(tmp_path, dataset, field):
    del dataset[0]["sources"][0][field]
    assert_rejected_before_database(tmp_path, dataset, f".sources[0].{field}")


@pytest.mark.parametrize("field", ["title", "url", "checked_on", "supports"])
@pytest.mark.parametrize("value", ["", " \t", None, 123])
def test_invalid_source_text(tmp_path, dataset, field, value):
    dataset[0]["sources"][0][field] = value
    assert_rejected_before_database(tmp_path, dataset, f".sources[0].{field}")


@pytest.mark.parametrize("url", [
    "file:///private", "ftp://example.com/product", "https:///missing-host",
    "https://", "not a URL", "https://exa mple.com", "https://example.com:bad",
    "https://[broken", "https://example.com\n/path", "https:\\example.com",
])
def test_invalid_url(tmp_path, dataset, url):
    dataset[0]["sources"][0]["url"] = url
    assert_rejected_before_database(tmp_path, dataset, ".sources[0].url")


@pytest.mark.parametrize("checked_on", [
    "2026-13-01", "2026-02-30", "2025-02-29", "20261009",
    "2026-1-9", "2026-10-09T00:00:00", "2026-W01-1",
])
def test_invalid_date(tmp_path, dataset, checked_on):
    dataset[0]["sources"][0]["checked_on"] = checked_on
    assert_rejected_before_database(tmp_path, dataset, ".sources[0].checked_on")


@pytest.mark.parametrize("urls", [
    ("https://example.com/a", "https://example.com/a"),
    ("https://EXAMPLE.com", "https://example.com/"),
])
def test_duplicate_source_url(tmp_path, dataset, urls):
    for source, url in zip(dataset[0]["sources"], urls):
        source["url"] = url
    assert_rejected_before_database(tmp_path, dataset, ".sources[1].url: duplicate")


@pytest.mark.parametrize("data", [{}, None, "products", 1, [None], [[]], ["product"]])
def test_invalid_dataset_structure(tmp_path, data):
    assert_rejected_before_database(tmp_path, data, "expected")


def test_invalid_json_syntax(tmp_path):
    curated = tmp_path / "broken.json"
    curated.write_text('[{"ean":', encoding="utf-8")
    with pytest.raises(CuratedDataError, match="line 1 column"):
        initialize_database(tmp_path / "new.sqlite3", curated)
    assert not (tmp_path / "new.sqlite3").exists()


def test_late_invalid_product_preserves_legacy_database(tmp_path, dataset):
    database = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("""CREATE TABLE products (
            ean TEXT PRIMARY KEY, product_name TEXT NOT NULL,
            brand TEXT NOT NULL, company TEXT NOT NULL)""")
        connection.execute("INSERT INTO products VALUES (?, ?, ?, ?)",
                           ("2000000000039", "Local", "Local", "Local"))
    before = database.read_bytes()
    second = copy.deepcopy(dataset[0])
    second["ean"] = "96385074"
    second["sources"][-1]["checked_on"] = "2026-02-30"
    dataset.append(second)
    curated = tmp_path / "curated.json"
    curated.write_text(json.dumps(dataset), encoding="utf-8")
    with pytest.raises(CuratedDataError, match=r"products\[1\].*checked_on"):
        initialize_database(database, curated)
    # No first-product/source insert, demo seed, or schema upgrade occurred.
    assert database.read_bytes() == before


def test_valid_ean8_null_role_and_empty_sources_import(tmp_path, dataset):
    dataset[0].update(ean="96385074", company_role=None, sources=[])
    curated = tmp_path / "curated.json"
    curated.write_text(json.dumps(dataset), encoding="utf-8")
    database = tmp_path / "valid.sqlite3"
    for _ in range(2):
        initialize_database(database, curated)
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT company_role FROM products WHERE ean = '96385074'"
        ).fetchone() == (None,)
        assert connection.execute("SELECT COUNT(*) FROM products").fetchone() == (4,)


def test_valid_sources_preserve_original_text_and_urls(dataset):
    dataset[0]["sources"][0].update(
        url="http://example.com/product", checked_on="2024-02-29", title=" Yhtiö "
    )
    second = copy.deepcopy(dataset[0])
    second["ean"] = "96385074"
    dataset.append(second)  # The same source URL on different products is valid.
    original = copy.deepcopy(dataset)
    assert validate_dataset(dataset) == original


@pytest.mark.parametrize("invalid", [False, True])
def test_validation_module_command(tmp_path, invalid):
    arguments = []
    if invalid:
        path = tmp_path / "bad.json"
        path.write_text('{}', encoding="utf-8")
        arguments = [str(path)]
    environment = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    result = subprocess.run(
        [sys.executable, "-B", "-m", "app.validate_curated", *arguments],
        cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == (1 if invalid else 0)
    if invalid:
        assert "dataset: expected a JSON list" in result.stderr
    else:
        assert "Valid curated dataset:" in result.stdout
    assert not list(tmp_path.glob("*.sqlite3"))
