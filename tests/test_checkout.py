"""Тести оформлення замовлення (checkout): бізнес-логіка, обмеження складу."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.orders.models import Order


@pytest.mark.django_db
def test_checkout_requires_login(client, product):
    """Неавторизований користувач має бути перенаправлений на логін."""
    session = client.session
    session["cart"] = {str(product.id): {"quantity": 1}}
    session.save()

    response = client.get(reverse("orders:checkout"))

    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_checkout_creates_order_and_reduces_stock(client, django_user_model, product):
    user = django_user_model.objects.create_user(username="carl", password="StrongPass123")
    client.force_login(user)

    session = client.session
    session["cart"] = {str(product.id): {"quantity": 3}}
    session.save()

    response = client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Carl Brewer",
            "email": "carl@example.com",
            "phone": "+380501234567",
            "shipping_address": "Kyiv, Khreshchatyk 1",
            "payment_method": "cod",
        },
    )

    assert response.status_code == 302
    order = Order.objects.get(user=user)
    assert order.items.count() == 1
    assert order.items.first().quantity == 3

    product.refresh_from_db()
    assert product.stock == 7  # було 10, замовили 3


@pytest.mark.django_db
def test_checkout_blocked_when_exceeds_stock(client, django_user_model, product):
    """Не можна оформити замовлення, якщо в кошику більше товару, ніж є на складі."""
    user = django_user_model.objects.create_user(username="dave", password="StrongPass123")
    client.force_login(user)

    session = client.session
    session["cart"] = {str(product.id): {"quantity": 999}}
    session.save()

    client.post(
        reverse("orders:checkout"),
        {
            "full_name": "Dave",
            "email": "dave@example.com",
            "phone": "+380501234567",
            "shipping_address": "Lviv",
            "payment_method": "cod",
        },
    )

    assert Order.objects.filter(user=user).count() == 0
