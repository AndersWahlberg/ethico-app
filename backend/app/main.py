"""Ethico's health and EAN lookup endpoints."""
import re
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from app.database import DATABASE_PATH, find_product, initialize_database


class ProductSource(BaseModel):
    title: str
    url: HttpUrl
    checked_on: date
    supports: str


class Product(BaseModel):
    ean: str
    product_name: str
    brand: str
    company: str
    company_role: str | None
    is_demo: bool
    sources: list[ProductSource]


def is_valid_ean(ean: str) -> bool:
    """Accept EAN-8 or EAN-13 with a correct check digit."""
    if not re.fullmatch(r"(?:[0-9]{8}|[0-9]{13})", ean):
        return False
    total = sum(int(digit) * (3 if index % 2 == 0 else 1)
                for index, digit in enumerate(reversed(ean[:-1])))
    return (10 - total % 10) % 10 == int(ean[-1])


def create_app(database_path: Path = DATABASE_PATH) -> FastAPI:
    # Tests supply a temporary database path to keep local data untouched.
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize_database(database_path)
        yield

    api = FastAPI(title="Ethico API", version="0.3.0", lifespan=lifespan)

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/products/{ean}", response_model=Product)
    def get_product(ean: str) -> dict[str, Any]:
        if not is_valid_ean(ean):
            raise HTTPException(422, "Enter a valid EAN-8 or EAN-13, including its check digit.")
        product = find_product(database_path, ean)
        if product is None:
            raise HTTPException(404, "Product not found in the local dataset.")
        return product

    return api


app = create_app()
