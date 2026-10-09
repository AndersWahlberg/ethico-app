import json
import sqlite3
from datetime import datetime, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app.database import find_product
from app.main import create_app
from app.open_food_facts import OpenFoodFactsProvider

EAN = "2000000000039"


def found(**changes):
    product = {"code": EAN, "product_name": "Crème Äänekoski", "brands": "Mäkelä, München"}
    product.update(changes)
    return {"status": "success", "product": product}


@pytest.fixture
def lookup(tmp_path):
    def run(handler, ean=EAN):
        requests = []

        def capture(request):
            requests.append(request)
            return handler(request)

        provider = OpenFoodFactsProvider(httpx.MockTransport(capture))
        path = tmp_path / "products.sqlite3"
        with TestClient(create_app(path, provider)) as client:
            response = client.get(f"/products/{ean}")
        return response, requests, path

    return run


@pytest.mark.parametrize("ean", ["2000000000015", "6430051512933"])
def test_local_hit_never_calls_provider(lookup, ean):
    def unexpected(_):
        pytest.fail("Local hit must not make an external request")

    response, requests, path = lookup(unexpected, ean)
    assert response.status_code == 200
    assert response.json() == find_product(path, ean)
    assert requests == []


def test_invalid_ean_never_calls_provider(lookup):
    response, requests, _ = lookup(lambda _: pytest.fail("Invalid EAN sent"), "2000000000016")
    assert response.status_code == 422
    assert requests == []


def test_external_mapping_provenance_utf8_and_request_contract(lookup):
    before = datetime.now(timezone.utc).date().isoformat()
    response, requests, path = lookup(lambda _: httpx.Response(
        200, content=json.dumps(found(), ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    ))
    after = datetime.now(timezone.utc).date().isoformat()
    assert response.status_code == 200
    product = response.json()
    assert product["ean"] == EAN
    assert product["product_name"] == "Crème Äänekoski"
    assert product["brand"] == "Mäkelä, München"
    assert product["company"] is None
    assert product["company_role"] is None
    assert product["is_demo"] is False
    assert len(product["sources"]) == 1
    source = product["sources"][0]
    assert source["title"] == source["provider"] == "Open Food Facts"
    assert source["url"] == f"https://world.openfoodfacts.org/product/{EAN}"
    assert source["license"] == "ODbL 1.0"
    assert source["checked_on"] is None
    assert source["retrieved_on"] in (before, after)
    assert source["supports"] == (
        "Product name and brand as reported by Open Food Facts. "
        "Company identity and ethical claims are not resolved by this source."
    )
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "GET"
    assert str(request.url).split("?")[0] == f"https://world.openfoodfacts.org/api/v3/product/{EAN}"
    assert dict(request.url.params) == {"fields": "code,product_name,brands"}
    assert request.headers["User-Agent"] == (
        "Ethico/0.3.0 (https://github.com/AndersWahlberg/my-new-project)"
    )
    assert request.content == b""
    assert "authorization" not in request.headers
    assert "cookie" not in request.headers
    assert all(value == 3.0 for value in request.extensions["timeout"].values())
    assert find_product(path, EAN) is None
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 4
        assert db.execute("SELECT COUNT(*) FROM product_sources").fetchone()[0] == 2


def test_external_result_is_not_cached(lookup):
    for _ in range(2):
        response, requests, path = lookup(lambda _: httpx.Response(200, json=found()))
        assert response.status_code == 200
        assert len(requests) == 1
        assert find_product(path, EAN) is None


def test_external_not_found(lookup):
    response, requests, _ = lookup(lambda _: httpx.Response(404))
    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found."}
    assert len(requests) == 1


@pytest.mark.parametrize("status", [429, 500, 502, 503, 302, 403])
def test_upstream_failure_and_redirect_are_not_not_found_or_retried(lookup, status):
    response, requests, _ = lookup(lambda _: httpx.Response(
        status, headers={"Location": "http://other.example/product"}, text="private upstream error",
    ))
    assert_temporary_failure(response, requests)


def assert_temporary_failure(response, requests):
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Product information could not be checked right now. Please try again."
    }
    assert len(requests) == 1


@pytest.mark.parametrize("error", [httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError])
def test_timeout_and_network_error(lookup, error):
    def unavailable(request):
        raise error("private upstream error", request=request)

    response, requests, _ = lookup(unavailable)
    assert_temporary_failure(response, requests)


@pytest.mark.parametrize("body", [b"not json", b"\xff", b"[]", b"null"])
def test_malformed_response(lookup, body):
    response, requests, _ = lookup(lambda _: httpx.Response(200, content=body))
    assert_temporary_failure(response, requests)


@pytest.mark.parametrize("payload", [
    {}, {"status": 1, "product": found()["product"]},
    {"status": "failure", "product": found()["product"]},
    {"status": "success_with_errors", "product": found()["product"]},
    {"status": "success", "product": None},
    found(code=None), found(code=2000000000039), found(code="2000000000022"),
    found(product_name=None), found(product_name=""), found(product_name=" \t"),
    found(product_name=42), found(brands=["Unexpected shape"]),
])
def test_unusable_identity_or_schema_is_temporary_failure(lookup, payload):
    response, requests, _ = lookup(lambda _: httpx.Response(200, json=payload))
    assert_temporary_failure(response, requests)


@pytest.mark.parametrize("brand", [None, "", " \t"])
def test_missing_brand_is_unknown(lookup, brand):
    payload = found(brands=brand)
    if brand is None:
        del payload["product"]["brands"]
    response, _, _ = lookup(lambda _: httpx.Response(200, json=payload))
    assert response.status_code == 200
    assert response.json()["brand"] is None
    assert response.json()["company"] is None


def test_provider_normalization_preserves_requested_ean(lookup):
    response, _, _ = lookup(
        lambda _: httpx.Response(200, json=found(code="96385074")), "0000096385074",
    )
    assert response.status_code == 200
    assert response.json()["ean"] == "0000096385074"
    assert response.json()["sources"][0]["url"].endswith("/96385074")


def test_success_with_warnings_can_contain_usable_identity(lookup):
    payload = found()
    payload["status"] = "success_with_warnings"
    response, _, _ = lookup(lambda _: httpx.Response(200, json=payload))
    assert response.status_code == 200
