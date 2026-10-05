"""Тести кошика (session-based cart)."""

from __future__ import annotations

import pytest
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from apps.orders.cart import Cart


def _build_request():
    """Створює HttpRequest з підключеною session-мідлварою (для тестів поза Django test client)."""
    request = RequestFactory().get("/")
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request


@pytest.mark.django_db
def test_cart_add_product(product):
    request = _build_request()
    cart = Cart(request)

    cart.add(product, quantity=2)

    assert len(cart) == 2
    assert cart.get_total_price() == product.price * 2


@pytest.mark.django_db
def test_cart_cannot_exceed_stock(product):
    """Кошик не повинен дозволяти покласти більше товару, ніж є на складі."""
    request = _build_request()
    cart = Cart(request)

    cart.add(product, quantity=999)  # product.stock == 10

    items = list(cart)
    assert items[0]["quantity"] == product.stock


@pytest.mark.django_db
def test_cart_remove_product(product):
    request = _build_request()
    cart = Cart(request)
    cart.add(product, quantity=1)

    cart.remove(product)

    assert len(cart) == 0


@pytest.mark.django_db
def test_cart_clear(product):
    request = _build_request()
    cart = Cart(request)
    cart.add(product, quantity=3)

    cart.clear()

    assert len(cart) == 0
