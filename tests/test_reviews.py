"""Тести відгуків: дозволено залишати лише після покупки товару."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.orders.models import Order, OrderItem
from apps.reviews.models import Review


@pytest.mark.django_db
def test_review_forbidden_without_purchase(client, user, product):
    client.force_login(user)

    response = client.post(
        reverse("products:product_detail", kwargs={"slug": product.slug}),
        {"rating": 5, "comment": "Чудовий товар!"},
    )

    assert response.status_code == 302
    assert Review.objects.count() == 0


@pytest.mark.django_db
def test_review_allowed_after_purchase(client, user, product):
    order = Order.objects.create(
        user=user, full_name="Alice", email="alice@example.com",
        phone="+380501234567", shipping_address="Kyiv",
    )
    OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)

    client.force_login(user)
    response = client.post(
        reverse("products:product_detail", kwargs={"slug": product.slug}),
        {"rating": 5, "comment": "Чудовий товар!"},
    )

    assert response.status_code == 302
    assert Review.objects.filter(product=product, user=user).exists()


@pytest.mark.django_db
def test_cannot_review_twice(client, user, product):
    order = Order.objects.create(
        user=user, full_name="Alice", email="alice@example.com",
        phone="+380501234567", shipping_address="Kyiv",
    )
    OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
    Review.objects.create(product=product, user=user, rating=4, comment="Добре")

    client.force_login(user)
    client.post(
        reverse("products:product_detail", kwargs={"slug": product.slug}),
        {"rating": 5, "comment": "Ще раз!"},
    )

    assert Review.objects.filter(product=product, user=user).count() == 1
