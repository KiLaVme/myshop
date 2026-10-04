"""Моделі каталогу товарів: Category та Product.

Крок 2 дорожньої карти - лише моделі (без views/фільтрів/каталогу,
вони з'являться на Кроці 3).
"""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Категорія товару, підтримує вкладеність (self-FK) для дерева категорій."""

    name = models.CharField("Назва", max_length=100)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="Батьківська категорія",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Автогенерація slug з назви, якщо його не задано вручну."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Товар каталогу."""

    name = models.CharField("Назва", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True, blank=True)
    description = models.TextField("Опис", blank=True)
    price = models.DecimalField("Ціна", max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        verbose_name="Категорія",
        on_delete=models.PROTECT,
        related_name="products",
    )
    image = models.ImageField("Зображення", upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField("Активний", default=True)
    stock = models.PositiveIntegerField("Залишок на складі", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "category"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self) -> bool:
        """Чи є товар в наявності хоча б в одній одиниці."""
        return self.stock > 0
