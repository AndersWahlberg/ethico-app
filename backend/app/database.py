"""SQLite storage, demo fixtures, and a small manually reviewed dataset."""
import json
import sqlite3
from pathlib import Path
from typing import Any

DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "ethico.sqlite3"
CURATED_PRODUCTS_PATH = Path(__file__).with_name("curated_products.json")
DEMO_PRODUCTS = [
    ("2000000000015", "Demo Oat Drink", "Demo Meadow", "Fictional Meadow Foods"),
    ("2000000000022", "Demo Hand Soap", "Demo River", "Fictional River Care"),
    ("0000000000017", "Demo Tea", "Demo Leaf", "Fictional Leaf Foods"),
]


def initialize_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            # Include schema changes and imported evidence in one transaction.
            connection.execute("BEGIN")
            connection.execute("""CREATE TABLE IF NOT EXISTS products (
                ean TEXT PRIMARY KEY, product_name TEXT NOT NULL,
                brand TEXT NOT NULL, company TEXT NOT NULL)""")
            # Upgrade the original four-column database without deleting rows.
            columns = {row[1] for row in connection.execute("PRAGMA table_info(products)")}
            if "company_role" not in columns:
                connection.execute("ALTER TABLE products ADD COLUMN company_role TEXT")
            if "is_demo" not in columns:
                connection.execute(
                    "ALTER TABLE products ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0"
                )
                connection.executemany(
                    "UPDATE products SET is_demo = 1 WHERE ean = ?",
                    [(product[0],) for product in DEMO_PRODUCTS],
                )
            connection.execute("""CREATE TABLE IF NOT EXISTS product_sources (
                ean TEXT NOT NULL REFERENCES products(ean) ON DELETE CASCADE,
                title TEXT NOT NULL, url TEXT NOT NULL,
                checked_on TEXT NOT NULL, supports TEXT NOT NULL,
                PRIMARY KEY (ean, url))""")
            connection.executemany(
                """INSERT OR IGNORE INTO products
                (ean, product_name, brand, company, is_demo) VALUES (?, ?, ?, ?, 1)""",
                DEMO_PRODUCTS,
            )
            for product in json.loads(CURATED_PRODUCTS_PATH.read_text(encoding="utf-8")):
                inserted = connection.execute(
                    """INSERT OR IGNORE INTO products
                    (ean, product_name, brand, company, company_role, is_demo)
                    VALUES (?, ?, ?, ?, ?, 0)""",
                    (product["ean"], product["product_name"], product["brand"],
                     product["company"], product["company_role"]),
                )
                # Sources accompany a newly imported row. Do not attach evidence
                # to a pre-existing row whose facts might have been edited.
                if inserted.rowcount:
                    connection.executemany(
                        """INSERT INTO product_sources
                        (ean, title, url, checked_on, supports) VALUES (?, ?, ?, ?, ?)""",
                        [(product["ean"], source["title"], source["url"],
                          source["checked_on"], source["supports"])
                         for source in product["sources"]],
                    )
    finally:
        connection.close()


def find_product(path: Path, ean: str) -> dict[str, Any] | None:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            """SELECT ean, product_name, brand, company, company_role, is_demo
            FROM products WHERE ean = ?""",
            (ean,),
        ).fetchone()
        if row is None:
            return None
        product = dict(row)
        product["is_demo"] = bool(product["is_demo"])
        product["sources"] = [dict(source) for source in connection.execute(
            """SELECT title, url, checked_on, supports FROM product_sources
            WHERE ean = ? ORDER BY url""", (ean,),
        )]
        return product
    finally:
        connection.close()
