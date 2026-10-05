"""Моделі каталогу товарів: Category та Product."""

from __future__ import annotations

from typing import TYPE_CHECKING
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ProductQuerySet(models.QuerySet["Product"]):
    """Кастомний QuerySet з корисними для каталогу фільтрами/анотаціями."""

    def active(self) -> ProductQuerySet:
        """Тільки товари, доступні для показу в каталозі."""
        return self.filter(is_active=True)

    def with_rating(self) -> ProductQuerySet:
        """Додає середній рейтинг та кількість відгуків - для сортування/показу."""
        return self.annotate(
            avg_rating=models.Avg("reviews__rating"),
            reviews_count=models.Count("reviews", distinct=True),
        )


# Створюємо клас менеджера явно через from_queryset
ProductManager = models.Manager.from_queryset(ProductQuerySet)


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

    # Вказуємо тип менеджера для mypy / django-stubs
    if TYPE_CHECKING:
        products: models.Manager[Product]

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

    # Єдине визначення менеджера
    objects = ProductManager()

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

    def get_absolute_url(self) -> str:
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def in_stock(self) -> bool:
        """Чи є товар в наявності хоча б в одній одиниці."""
        return self.stock > 0
