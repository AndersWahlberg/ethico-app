"""Validate curated JSON without changing facts or accessing a database."""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from pydantic import HttpUrl

from app.ean import is_valid_ean

CURATED_PRODUCTS_PATH = Path(__file__).with_name("curated_products.json")


class CuratedDataError(ValueError):
    """Invalid curated data, with a location suitable for a human editor."""


def _text(record: dict, field: str, location: str) -> str:
    if field not in record:
        raise CuratedDataError(f"{location}.{field}: required field is missing")
    value = record[field]
    if not isinstance(value, str) or not value.strip():
        raise CuratedDataError(f"{location}.{field}: expected a non-empty string")
    return value


def _url(value: str, location: str) -> str:
    try:
        # Do not let URL parsers repair whitespace, backslashes or missing //.
        if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError("whitespace/control character")
        if "\\" in value:
            raise ValueError("backslash")
        parts = urlsplit(value)
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
            raise ValueError("scheme/host")
        validated = HttpUrl(value)
        if not validated.host:
            raise ValueError("host")
        return str(validated)
    except ValueError as error:
        raise CuratedDataError(
            f"{location}.url: expected a valid HTTP(S) URL with a host"
        ) from error


def validate_dataset(data: Any) -> list[dict[str, Any]]:
    """Check every entry before returning the original, unmodified dataset."""
    if not isinstance(data, list):
        raise CuratedDataError("dataset: expected a JSON list of product objects")
    eans: set[str] = set()
    for index, product in enumerate(data):
        location = f"products[{index}]"
        if not isinstance(product, dict):
            raise CuratedDataError(f"{location}: expected a product object")
        ean = _text(product, "ean", location)
        if not is_valid_ean(ean):
            raise CuratedDataError(
                f"{location}.ean: expected EAN-8 or EAN-13 ASCII digits with a valid check digit"
            )
        if ean in eans:
            raise CuratedDataError(f"{location}.ean: duplicate EAN {ean}")
        eans.add(ean)
        location += f" (EAN {ean})"
        for field in ("product_name", "brand", "company"):
            _text(product, field, location)
        if "company_role" not in product:
            raise CuratedDataError(f"{location}.company_role: required field is missing")
        if product["company_role"] is not None:
            _text(product, "company_role", location)
        if "sources" not in product or not isinstance(product["sources"], list):
            raise CuratedDataError(f"{location}.sources: expected a list (field is required)")
        urls: set[str] = set()
        for source_index, source in enumerate(product["sources"]):
            source_location = f"{location}.sources[{source_index}]"
            if not isinstance(source, dict):
                raise CuratedDataError(f"{source_location}: expected a source object")
            for field in ("title", "supports"):
                _text(source, field, source_location)
            url = _url(_text(source, "url", source_location), source_location)
            if url in urls:
                raise CuratedDataError(f"{source_location}.url: duplicate source URL {url}")
            urls.add(url)
            checked_on = _text(source, "checked_on", source_location)
            try:
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", checked_on):
                    raise ValueError("date format")
                date.fromisoformat(checked_on)
            except ValueError as error:
                raise CuratedDataError(
                    f"{source_location}.checked_on: expected a valid YYYY-MM-DD calendar date"
                ) from error
    return data


def load_curated_products(path: Path = CURATED_PRODUCTS_PATH) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CuratedDataError(f"{path}: cannot read UTF-8 JSON: {error}") from error
    try:
        return validate_dataset(data)
    except CuratedDataError as error:
        raise CuratedDataError(f"{path}: {error}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=CURATED_PRODUCTS_PATH)
    args = parser.parse_args()
    try:
        products = load_curated_products(args.path)
    except CuratedDataError as error:
        print(f"Invalid curated dataset: {error}", file=sys.stderr)
        return 1
    print(f"Valid curated dataset: {len(products)} product(s) in {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
