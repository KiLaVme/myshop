"""Спільні pytest-фікстури для всіх тестів проекту."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.products.models import Category, Product


@pytest.fixture
def category(db) -> Category:
    """Тестова категорія."""
    return Category.objects.create(name="Hops", slug="hops")


@pytest.fixture
def product(db, category: Category) -> Product:
    """Тестовий товар з достатнім залишком на складі."""
    return Product.objects.create(
        name="Citra Hops",
        slug="citra-hops",
        description="Ideal for IPAs",
        price=Decimal("5.99"),
        category=category,
        stock=10,
        is_active=True,
    )


@pytest.fixture
def user(db) -> User:
    """Звичайний користувач."""
    return User.objects.create_user(username="alice", password="StrongPass123", email="alice@example.com")


@pytest.fixture
def other_user(db) -> User:
    """Другий користувач - для перевірки ізоляції даних (permissions)."""
    return User.objects.create_user(username="bob", password="StrongPass123", email="bob@example.com")


@pytest.fixture
def api_client() -> APIClient:
    """Неавтентифікований API-клієнт DRF."""
    return APIClient()


@pytest.fixture
def auth_api_client(api_client: APIClient, user: User) -> APIClient:
    """API-клієнт, авторизований через JWT access-токен."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client
