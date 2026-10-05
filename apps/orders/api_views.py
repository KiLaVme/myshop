"""REST API view-класи для кошика та замовлень."""

from __future__ import annotations

from typing import cast
from django.contrib.auth.models import User
from rest_framework import serializers

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product

from .cart import Cart
from .models import Order, OrderItem
from .serializers import CartItemInputSerializer, OrderCreateSerializer, OrderSerializer


class CartAPIView(APIView):
    """GET/POST /api/cart/ - перегляд та додавання товару в кошик (сесія)."""

    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemInputSerializer  # лише для коректної генерації Swagger-схеми

    def get(self, request: Request) -> Response:
        cart = Cart(request)
        items = [
            {
                "product_id": item["product"].id,
                "name": item["product"].name,
                "price": str(item["price"]),
                "quantity": item["quantity"],
                "total_price": str(item["total_price"]),
                "exceeds_stock": item["exceeds_stock"],
            }
            for item in cart
        ]
        return Response({"items": items, "total_price": str(cart.get_total_price())})

    def post(self, request: Request) -> Response:
        serializer = CartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product: Product = serializer.validated_data["product"]
        quantity: int = serializer.validated_data["quantity"]

        cart = Cart(request)
        cart.add(product=product, quantity=quantity)
        return Response(status=status.HTTP_201_CREATED)


class CartItemAPIView(APIView):
    """PATCH/DELETE /api/cart/<product_id>/ - зміна кількості або видалення позиції."""

    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemInputSerializer  # лише для коректної генерації Swagger-схеми

    def patch(self, request: Request, product_id: int) -> Response:
        product = get_object_or_404(Product, pk=product_id)
        quantity = request.data.get("quantity")
        if quantity is None or int(quantity) < 1:
            return Response({"detail": "quantity must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart(request)
        cart.add(product=product, quantity=int(quantity), override_quantity=True)
        return Response(status=status.HTTP_200_OK)

    def delete(self, request: Request, product_id: int) -> Response:
        product = get_object_or_404(Product, pk=product_id)
        cart = Cart(request)
        cart.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    """CRUD замовлень поточного користувача.

    - GET /api/orders/       -> список СВОЇХ замовлень
    - POST /api/orders/      -> створити замовлення на основі кошика в сесії
    - GET /api/orders/<id>/  -> деталі СВОГО замовлення
    - PATCH/PUT/DELETE       -> оновлення статусу / скасування свого замовлення
    """

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_queryset(self):
        """Користувач бачить лише свої замовлення (ключова вимога ТЗ)."""
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()

        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        """Створює замовлення з поточного кошика сесії (аналогічно web-checkout)."""
        order_serializer = cast(OrderSerializer, serializer)
        user = cast(User, self.request.user)
        cart = Cart(self.request)
        if len(cart) == 0:
            raise serializers.ValidationError({"detail": "Кошик порожній."})
        if cart.has_stock_issues():
            raise serializers.ValidationError({"detail": "Недостатньо товару на складі."})

        with transaction.atomic():
            order = order_serializer.save(user=user)
            for item in cart:
                product = item["product"]
                OrderItem.objects.create(
                    order=order, product=product, quantity=item["quantity"], price=item["price"]
                )
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])
            order.recalculate_total()

        cart.clear()

    def perform_update(self, serializer) -> None:
        """Дозволяємо користувачу лише скасувати замовлення (status=cancelled)."""
        new_status = self.request.data.get("status")
        if new_status and new_status != Order.Status.CANCELLED:
            raise serializer.ValidationError(
                {"status": "Через API користувач може лише скасувати замовлення."}
            )
        serializer.save()
