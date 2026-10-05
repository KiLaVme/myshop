"""Серіалізатори REST API для товарів та категорій."""

from __future__ import annotations

from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent"]


class ProductListSerializer(serializers.ModelSerializer):
    """Полегшений серіалізатор для списку товарів (GET /api/products/)."""

    category: serializers.Field = serializers.SlugRelatedField(
        slug_field="slug", read_only=True
    )
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "category", "image",
            "is_active", "stock", "avg_rating",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Повний серіалізатор для деталей товару (GET /api/products/<id>/)."""

    category = CategorySerializer(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "price", "category",
            "image", "is_active", "stock", "avg_rating", "reviews_count",
            "created_at", "updated_at",
        ]
