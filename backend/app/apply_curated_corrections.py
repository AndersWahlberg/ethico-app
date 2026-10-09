"""Validate, preview, or explicitly apply reviewed corrections to existing SQLite."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from app.database import DATABASE_PATH, DEMO_PRODUCTS
from app.validate_curated import (
    CURATED_PRODUCTS_PATH, CuratedDataError, load_curated_products, validate_dataset,
)

CORRECTIONS_PATH = Path(__file__).with_name("curated_corrections.json")
PRODUCT_FIELDS = ("ean", "product_name", "brand", "company", "company_role")
SOURCE_FIELDS = ("title", "url", "checked_on", "supports")


def reviewed_state(product: dict[str, Any]) -> dict[str, Any]:
    """Compare stored fields exactly; only source list order is insignificant."""
    return {
        **{field: product[field] for field in PRODUCT_FIELDS},
        "sources": sorted(
            ({field: source[field] for field in SOURCE_FIELDS}
             for source in product["sources"]),
            key=lambda source: source["url"],
        ),
    }


def load_corrections(
    curated_path: Path = CURATED_PRODUCTS_PATH,
    corrections_path: Path = CORRECTIONS_PATH,
) -> list[dict[str, Any]]:
    """Validate both complete files before any database connection is opened."""
    products = {p["ean"]: reviewed_state(p) for p in load_curated_products(curated_path)}
    try:
        data = json.loads(corrections_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CuratedDataError(f"{corrections_path}: cannot read UTF-8 JSON: {error}") from error
    if not isinstance(data, list):
        raise CuratedDataError(f"{corrections_path}: expected a JSON list of corrections")
    seen = set()
    demo_eans = {product[0] for product in DEMO_PRODUCTS}
    for index, correction in enumerate(data):
        location = f"{corrections_path}: corrections[{index}]"
        if not isinstance(correction, dict) or set(correction) != {
            "ean", "reason", "expected", "replacement"
        }:
            raise CuratedDataError(
                f"{location}: expected exactly ean, reason, expected and replacement"
            )
        reason = correction["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise CuratedDataError(f"{location}.reason: expected a non-empty string")
        for side in ("expected", "replacement"):
            product = correction[side]
            try:
                validate_dataset([product])
                if set(product) != {*PRODUCT_FIELDS, "sources"}:
                    raise CuratedDataError("product must contain only the reviewed SQLite fields")
                if any(set(source) != set(SOURCE_FIELDS) for source in product["sources"]):
                    raise CuratedDataError("sources must contain only title, url, checked_on, supports")
            except CuratedDataError as error:
                raise CuratedDataError(f"{location}.{side}: {error}") from error
            if correction["ean"] != product["ean"]:
                raise CuratedDataError(f"{location}.{side}.ean: must equal correction EAN")
        ean = correction["ean"]
        if ean in demo_eans:
            raise CuratedDataError(f"{location}: demo EAN {ean} cannot be corrected")
        if ean in seen:
            raise CuratedDataError(f"{location}: duplicate correction EAN {ean}")
        seen.add(ean)
        if reviewed_state(correction["replacement"]) != products.get(ean):
            raise CuratedDataError(
                f"{location}: replacement must match the current curated product {ean}"
            )
    return data


def _current_state(connection: sqlite3.Connection, ean: str) -> dict[str, Any] | None:
    row = connection.execute(
        """SELECT ean, product_name, brand, company, company_role, is_demo
        FROM products WHERE ean = ?""", (ean,),
    ).fetchone()
    if row is None:
        return None
    product = dict(row)
    product["sources"] = [dict(source) for source in connection.execute(
        """SELECT title, url, checked_on, supports FROM product_sources
        WHERE ean = ? ORDER BY url""", (ean,),
    )]
    return product


def run_corrections(
    database_path: Path = DATABASE_PATH,
    curated_path: Path = CURATED_PRODUCTS_PATH,
    corrections_path: Path = CORRECTIONS_PATH,
    *, apply: bool = False,
) -> list[dict[str, Any]]:
    corrections = load_corrections(curated_path, corrections_path)
    # URI modes prevent accidental database creation. Preview cannot write.
    uri = database_path.resolve().as_uri() + ("?mode=rw" if apply else "?mode=ro")
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            # Reserve the writer before inspecting any targets to prevent a
            # concurrent writer changing expected state between check and update.
            connection.execute("BEGIN IMMEDIATE" if apply else "BEGIN")
            results = []
            for correction in corrections:
                current = _current_state(connection, correction["ean"])
                if current is None:
                    outcome = "missing_product"
                elif current["is_demo"] != 0:
                    outcome = "conflict"
                elif reviewed_state(current) == reviewed_state(correction["replacement"]):
                    outcome = "already_applied"
                elif reviewed_state(current) == reviewed_state(correction["expected"]):
                    outcome = "needs_application"
                else:
                    outcome = "conflict"
                results.append({"ean": correction["ean"], "outcome": outcome,
                                "reason": correction["reason"]})
            unsafe = any(r["outcome"] in {"conflict", "missing_product"} for r in results)
            if apply and not unsafe:
                for correction, result in zip(corrections, results):
                    if result["outcome"] != "needs_application":
                        continue
                    product = correction["replacement"]
                    connection.execute(
                        """UPDATE products SET product_name = ?, brand = ?, company = ?,
                        company_role = ? WHERE ean = ?""",
                        (product["product_name"], product["brand"], product["company"],
                         product["company_role"], product["ean"]),
                    )
                    connection.execute("DELETE FROM product_sources WHERE ean = ?", (product["ean"],))
                    connection.executemany(
                        """INSERT INTO product_sources
                        (ean, title, url, checked_on, supports) VALUES (?, ?, ?, ?, ?)""",
                        [(product["ean"], source["title"], source["url"],
                          source["checked_on"], source["supports"])
                         for source in product["sources"]],
                    )
                    result["outcome"] = "applied"
            else:
                connection.rollback()
        # A commit failure raises before successful outcomes reach the caller.
        return results
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DATABASE_PATH)
    parser.add_argument("--curated", type=Path, default=CURATED_PRODUCTS_PATH)
    parser.add_argument("--corrections", type=Path, default=CORRECTIONS_PATH)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="explicitly apply the entire safe batch")
    mode.add_argument("--dry-run", action="store_true", help="read-only preview (default)")
    mode.add_argument("--validate-only", action="store_true", help="validate files without opening SQLite")
    args = parser.parse_args()
    try:
        if args.validate_only:
            corrections = load_corrections(args.curated, args.corrections)
            print(f"Valid correction registry: {len(corrections)} correction(s); no database accessed.")
            return 0
        results = run_corrections(args.database, args.curated, args.corrections, apply=args.apply)
    except CuratedDataError as error:
        print(f"Invalid correction data: {error}", file=sys.stderr)
        return 1
    except (sqlite3.Error, OSError, ValueError) as error:
        print(f"Database operation failed; no corrections committed: {error}", file=sys.stderr)
        return 1
    for result in results:
        print(f"{result['ean']}: {result['outcome']} — {result['reason']}")
    if any(r["outcome"] in {"conflict", "missing_product"} for r in results):
        print("Batch blocked: no corrections applied; review unexpected or missing local state.")
        return 2
    if args.apply:
        print(f"Applied {sum(r['outcome'] == 'applied' for r in results)} correction(s).")
    else:
        print("Preview only: needs_application would be applied; no changes made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
