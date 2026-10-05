"""Тести веб-каталогу товарів: список, пошук, фільтри, сторінка товару."""

from __future__ import annotations

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_catalog_page_returns_products(client, product):
    response = client.get(reverse("products:catalog"))

    assert response.status_code == 200
    assert product.name.encode() in response.content


@pytest.mark.django_db
def test_catalog_search_filters_by_name(client, product):
    response = client.get(reverse("products:catalog"), {"q": "Citra"})
    assert product in response.context["products"]

    response = client.get(reverse("products:catalog"), {"q": "NoSuchProduct"})
    assert product not in response.context["products"]


@pytest.mark.django_db
def test_product_detail_page(client, product):
    response = client.get(reverse("products:product_detail", kwargs={"slug": product.slug}))

    assert response.status_code == 200
    assert response.context["product"] == product
