"""Серіалізатори REST API для замовлень та кошика."""

from __future__ import annotations

from rest_framework import serializers

from apps.products.models import Product
from apps.products.serializers import ProductListSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price", "total"]


class OrderSerializer(serializers.ModelSerializer):
    """Серіалізатор замовлення для читання (список і деталі)."""

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "status", "total_price", "full_name", "email", "phone",
            "shipping_address", "payment_method", "items", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "total_price", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Серіалізатор створення замовлення на основі кошика (session-based)."""

    class Meta:
        model = Order
        fields = [
            "id", "full_name", "email", "phone", "shipping_address",
            "payment_method", "status", "total_price",
        ]
        read_only_fields = ["id", "status", "total_price"]


class CartItemInputSerializer(serializers.Serializer):
    """Вхідні дані для додавання/оновлення позиції кошика через API."""

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.active(), source="product"
    )
    quantity = serializers.IntegerField(min_value=1)
