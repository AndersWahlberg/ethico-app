"""SQLite storage and fictional demonstration products."""
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "ethico.sqlite3"
DEMO_PRODUCTS = [
    ("2000000000015", "Demo Oat Drink", "Demo Meadow", "Fictional Meadow Foods"),
    ("2000000000022", "Demo Hand Soap", "Demo River", "Fictional River Care"),
    ("0000000000017", "Demo Tea", "Demo Leaf", "Fictional Leaf Foods"),
]


def initialize_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        with connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS products (
                ean TEXT PRIMARY KEY, product_name TEXT NOT NULL,
                brand TEXT NOT NULL, company TEXT NOT NULL)""")
            connection.executemany(
                "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)", DEMO_PRODUCTS
            )
    finally:
        connection.close()


def find_product(path: Path, ean: str) -> dict[str, str] | None:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT ean, product_name, brand, company FROM products WHERE ean = ?",
            (ean,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()
