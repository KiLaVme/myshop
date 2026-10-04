"""Модель відгуку на товар.

Крок 2 дорожньої карти - лише модель. Логіка "відгук лише після покупки"
та відображення на сторінці товару з'являться на Кроці 4.
"""

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """Відгук користувача на товар з рейтингом 1-5."""

    product = models.ForeignKey(
        "products.Product",
        verbose_name="Товар",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        "Рейтинг",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("Коментар", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ["-created_at"]
        # Один користувач - один відгук на товар
        constraints = [
            models.UniqueConstraint(fields=["product", "user"], name="unique_review_per_user_product")
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.product} ({self.rating}/5)"
