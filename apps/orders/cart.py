"""Реалізація кошика на основі сесій Django (без окремої моделі в БД).

Структура даних, що зберігається в session[settings.CART_SESSION_ID]:
    {
        "<product_id>": {"quantity": int},
        ...
    }
Ціна навмисно НЕ зберігається в сесії - вона завжди береться "наживо"
з моделі Product, щоб уникнути розсинхронізації, якщо ціна товару зміниться.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Iterator

from django.conf import settings
from django.http import HttpRequest

from apps.products.models import Product


class Cart:
    """Обгортка над request.session для роботи з кошиком покупок."""

    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart: dict[str, dict] = cart

    def add(self, product: Product, quantity: int = 1, override_quantity: bool = False) -> None:
        """Додає товар у кошик або оновлює його кількість.

        Кількість обмежується наявним залишком на складі (product.stock),
        щоб неможливо було покласти в кошик більше, ніж є на складі.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0}

        if override_quantity:
            new_quantity = quantity
        else:
            new_quantity = self.cart[product_id]["quantity"] + quantity

        new_quantity = max(0, min(new_quantity, product.stock))

        if new_quantity == 0:
            self.remove(product)
            return

        self.cart[product_id]["quantity"] = new_quantity
        self.save()

    def remove(self, product: Product) -> None:
        """Видаляє товар з кошика повністю."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self) -> None:
        """Позначає сесію як змінену, щоб Django зберіг її."""
        self.session.modified = True

    def clear(self) -> None:
        """Повністю очищує кошик (використовується після оформлення замовлення)."""
        self.session[settings.CART_SESSION_ID] = {}
        self.save()

    def __iter__(self) -> Iterator[dict]:
        """Ітерується по товарах в кошику, підвантажуючи Product одним запитом."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}

        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if product is None:
                continue
            quantity = item["quantity"]
            yield {
                "product": product,
                "quantity": quantity,
                "price": product.price,
                "total_price": product.price * quantity,
                "exceeds_stock": quantity > product.stock,
            }

    def __len__(self) -> int:
        """Загальна кількість одиниць товару в кошику."""
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """Підсумкова вартість кошика."""
        total = Decimal("0")
        for item in self:
            total += item["total_price"]
        return total

    def has_stock_issues(self) -> bool:
        """True, якщо хоч одна позиція перевищує наявний залишок на складі."""
        return any(item["exceeds_stock"] for item in self)
