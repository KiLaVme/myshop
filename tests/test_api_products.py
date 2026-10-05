"""Тести REST API: товари (список, деталі, фільтрація, пошук)."""

from __future__ import annotations

import pytest


@pytest.mark.django_db
def test_product_list_api(api_client, product):
    response = api_client.get("/api/products/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == product.name


@pytest.mark.django_db
def test_product_detail_api(api_client, product):
    response = api_client.get(f"/api/products/{product.id}/")

    assert response.status_code == 200
    assert response.data["slug"] == product.slug


@pytest.mark.django_db
def test_product_search_api(api_client, product):
    response = api_client.get("/api/products/", {"search": "Citra"})
    assert response.data["count"] == 1

    response = api_client.get("/api/products/", {"search": "NoMatch"})
    assert response.data["count"] == 0


@pytest.mark.django_db
def test_product_price_filter_api(api_client, product):
    response = api_client.get("/api/products/", {"min_price": "100"})
    assert response.data["count"] == 0

    response = api_client.get("/api/products/", {"min_price": "1"})
    assert response.data["count"] == 1
