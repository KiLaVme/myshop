"""Моделі замовлень: Order та OrderItem.

Крок 2 дорожньої карти - лише моделі. Кошик (логіка на основі сесій),
views оформлення замовлення та email-сповіщення з'являться на Кроках 5-6.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models


class Order(models.Model):
    """Замовлення користувача."""

    class Status(models.TextChoices):
        PENDING = "pending", "Очікує оплати"
        PAID = "paid", "Оплачено"
        SHIPPED = "shipped", "Відправлено"
        DELIVERED = "delivered", "Доставлено"
        CANCELLED = "cancelled", "Скасовано"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Користувач",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.PENDING
    )
    total_price = models.DecimalField("Сума", max_digits=10, decimal_places=2, default=Decimal("0"))

    full_name = models.CharField("ПІБ отримувача", max_length=200)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=32)
    shipping_address = models.TextField("Адреса доставки")
    payment_method = models.CharField(
        "Спосіб оплати",
        max_length=20,
        choices=[("card", "Картка (мок)"), ("cod", "Оплата при отриманні")],
        default="cod",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Замовлення #{self.pk} ({self.user})"

    def recalculate_total(self) -> None:
        """Перераховує total_price на основі пов'язаних OrderItem та зберігає."""
        total = sum((item.price * item.quantity for item in self.items.all()), Decimal("0"))
        self.total_price = total
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    """Позиція замовлення - товар + кількість + ціна на момент покупки (снепшот)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField("Кількість", default=1)
    price = models.DecimalField(
        "Ціна на момент покупки", max_digits=10, decimal_places=2
    )

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"

    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"

    @property
    def total(self) -> Decimal:
        """Сума по позиції: ціна * кількість."""
        return self.price * self.quantity
