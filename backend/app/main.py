"""Ethico's health and EAN lookup endpoints."""
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from app import __version__
from app.database import DATABASE_PATH, find_product, initialize_database
from app.ean import is_valid_ean
from app.open_food_facts import ExternalLookupUnavailable, OpenFoodFactsProvider


class ProductSource(BaseModel):
    title: str
    url: HttpUrl
    checked_on: date | None = None
    supports: str
    provider: str | None = None
    retrieved_on: date | None = None
    license: str | None = None


class Product(BaseModel):
    ean: str
    product_name: str
    brand: str | None
    company: str | None
    company_role: str | None
    is_demo: bool
    sources: list[ProductSource]


def create_app(
    database_path: Path = DATABASE_PATH,
    off_provider: OpenFoodFactsProvider | None = None,
) -> FastAPI:
    provider = off_provider if off_provider is not None else OpenFoodFactsProvider()
    # Tests supply a temporary database path to keep local data untouched.
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize_database(database_path)
        yield

    api = FastAPI(title="Ethico API", version=__version__, lifespan=lifespan)

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/products/{ean}", response_model=Product, response_model_exclude_unset=True)
    def get_product(ean: str) -> dict[str, Any]:
        if not is_valid_ean(ean):
            raise HTTPException(422, "Enter a valid EAN-8 or EAN-13, including its check digit.")
        product = find_product(database_path, ean)
        if product is not None:
            return product
        try:
            product = provider.lookup(ean)
        except ExternalLookupUnavailable:
            raise HTTPException(
                503, "Product information could not be checked right now. Please try again."
            ) from None
        if product is None:
            raise HTTPException(404, "Product not found.")
        return product

    return api


app = create_app()
