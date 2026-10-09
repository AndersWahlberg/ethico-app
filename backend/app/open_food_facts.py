"""Read-only, uncached Open Food Facts product lookup; no company inference."""
from datetime import datetime, timezone
from typing import Any

import httpx

from app import __version__
from app.ean import is_valid_ean

# Identify the application and version without disclosing a developer identity,
# personal repository URL, email address, or other user-specific metadata.
USER_AGENT = f"Ethico/{__version__}"
TIMEOUT_SECONDS = 3.0


class ExternalLookupUnavailable(Exception):
    """The provider could not establish usable product information."""


class OpenFoodFactsProvider:
    def __init__(self, transport: httpx.BaseTransport | None = None):
        # MockTransport allows tests to exercise real parsing without network I/O.
        self.transport = transport

    def lookup(self, ean: str) -> dict[str, Any] | None:
        """Return a product, None for HTTP 404, or raise ExternalLookupUnavailable."""
        if not is_valid_ean(ean):
            raise ValueError("Expected a validated EAN")
        try:
            # One request; default transport has no retries. Do not follow redirects
            # to other product-type servers, or retain upstream cookies between users.
            with httpx.Client(
                transport=self.transport,
                timeout=TIMEOUT_SECONDS,
                follow_redirects=False,
                headers={"User-Agent": USER_AGENT},
            ) as client:
                response = client.get(
                    f"https://world.openfoodfacts.org/api/v3/product/{ean}",
                    params={"fields": "code,product_name,brands"},
                )
            if response.status_code == 404:
                return None
            if response.status_code != 200:
                raise ExternalLookupUnavailable()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as error:
            raise ExternalLookupUnavailable() from error

        if not isinstance(payload, dict) or payload.get("status") not in (
            "success", "success_with_warnings",
        ):
            raise ExternalLookupUnavailable()
        product = payload.get("product")
        if not isinstance(product, dict):
            raise ExternalLookupUnavailable()
        code = product.get("code")
        name = product.get("product_name")
        brand = product.get("brands")
        # OFF normalizes leading zeroes. Retain the requested EAN in Ethico, but
        # never accept a different identifier or invent a missing product name.
        if (
            not isinstance(code, str) or not is_valid_ean(code)
            or code.lstrip("0") != ean.lstrip("0")
            or not isinstance(name, str) or not name.strip()
            or (brand is not None and not isinstance(brand, str))
        ):
            raise ExternalLookupUnavailable()
        return {
            "ean": ean,
            "product_name": name,
            "brand": brand if brand and brand.strip() else None,
            "company": None,
            "company_role": None,
            "is_demo": False,
            "sources": [{
                "title": "Open Food Facts",
                "url": f"https://world.openfoodfacts.org/product/{code}",
                "provider": "Open Food Facts",
                "checked_on": None,
                "retrieved_on": datetime.now(timezone.utc).date().isoformat(),
                "license": "ODbL 1.0",
                "supports": (
                    "Product name and brand as reported by Open Food Facts. "
                    "Company identity and ethical claims are not resolved by this source."
                ),
            }],
        }
