"""Тести REST API: реєстрація, JWT-логін, доступ лише до своїх замовлень."""

from __future__ import annotations

import pytest

from apps.orders.models import Order


@pytest.mark.django_db
def test_register_api_returns_jwt_tokens(api_client):
    response = api_client.post(
        "/api/users/register/",
        {"username": "newuser", "email": "new@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    assert "access" in response.data["tokens"]
    assert "refresh" in response.data["tokens"]


@pytest.mark.django_db
def test_login_api_returns_jwt_tokens(api_client, user):
    response = api_client.post(
        "/api/users/login/", {"username": user.username, "password": "StrongPass123"}
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_api_wrong_password(api_client, user):
    response = api_client.post(
        "/api/users/login/", {"username": user.username, "password": "wrong"}
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_endpoint_requires_auth(api_client):
    response = api_client.get("/api/users/me/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_endpoint_returns_current_user(auth_api_client, user):
    response = auth_api_client.get("/api/users/me/")

    assert response.status_code == 200
    assert response.data["username"] == user.username


@pytest.mark.django_db
def test_user_sees_only_own_orders(auth_api_client, user, other_user, product):
    Order.objects.create(
        user=user, full_name="Alice", email="a@a.com", phone="+380501234567", shipping_address="Kyiv"
    )
    Order.objects.create(
        user=other_user, full_name="Bob", email="b@b.com", phone="+380501234567", shipping_address="Lviv"
    )

    response = auth_api_client.get("/api/orders/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["full_name"] == "Alice"
