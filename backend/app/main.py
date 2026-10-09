"""Ethico's health and EAN lookup endpoints."""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from app.database import DATABASE_PATH, find_product, initialize_database
from app.ean import is_valid_ean


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
