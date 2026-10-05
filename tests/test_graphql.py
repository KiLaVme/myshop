"""Тести GraphQL-схеми аналітики: доступ лише для персоналу, коректні дані."""

from __future__ import annotations

import json

import pytest

GRAPHQL_URL = "/graphql/"


def _query(client, query: str, variables: dict | None = None):
    return client.post(
        GRAPHQL_URL,
        data=json.dumps({"query": query, "variables": variables or {}}),
        content_type="application/json",
    )


@pytest.mark.django_db
def test_graphql_denies_anonymous_user(client):
    response = _query(client, "{ revenueSummary { totalRevenue ordersCount } }")

    body = response.json()
    assert response.status_code == 200
    assert "errors" in body
    assert "персоналу" in body["errors"][0]["message"]


@pytest.mark.django_db
def test_graphql_denies_regular_user(client, user):
    client.force_login(user)
    response = _query(client, "{ revenueSummary { totalRevenue ordersCount } }")

    body = response.json()
    assert "errors" in body


@pytest.mark.django_db
def test_graphql_revenue_summary_for_staff(client, django_user_model, product):
    from apps.orders.models import Order, OrderItem

    staff = django_user_model.objects.create_user(username="admin2", password="pass12345", is_staff=True)
    order = Order.objects.create(
        user=staff, full_name="Admin", email="admin2@example.com",
        phone="+380501234567", shipping_address="Kyiv", status=Order.Status.PAID,
    )
    OrderItem.objects.create(order=order, product=product, quantity=2, price=product.price)
    order.recalculate_total()

    client.force_login(staff)
    response = _query(client, "{ revenueSummary { totalRevenue ordersCount averageCheck } }")

    body = response.json()
    assert "errors" not in body
    data = body["data"]["revenueSummary"]
    assert data["ordersCount"] == 1
    assert float(data["totalRevenue"]) == float(product.price) * 2


@pytest.mark.django_db
def test_graphql_top_products_for_staff(client, django_user_model, product):
    from apps.orders.models import Order, OrderItem

    staff = django_user_model.objects.create_user(username="admin3", password="pass12345", is_staff=True)
    order = Order.objects.create(
        user=staff, full_name="Admin", email="admin3@example.com",
        phone="+380501234567", shipping_address="Kyiv",
    )
    OrderItem.objects.create(order=order, product=product, quantity=5, price=product.price)

    client.force_login(staff)
    response = _query(
        client,
        "{ topProducts(limit: 5) { productName totalQuantity totalRevenue } }",
    )

    body = response.json()
    assert "errors" not in body
    rows = body["data"]["topProducts"]
    assert rows[0]["productName"] == product.name
    assert rows[0]["totalQuantity"] == 5


@pytest.mark.django_db
def test_graphql_low_stock_products_for_staff(client, django_user_model, product):
    product.stock = 2
    product.save(update_fields=["stock"])

    staff = django_user_model.objects.create_user(username="admin4", password="pass12345", is_staff=True)
    client.force_login(staff)

    response = _query(client, "{ lowStockProducts(threshold: 5) { name stock } }")

    body = response.json()
    assert "errors" not in body
    names = [row["name"] for row in body["data"]["lowStockProducts"]]
    assert product.name in names
