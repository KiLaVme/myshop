"""REST API view-класи для відгуків: GET/POST /api/products/<id>/reviews/."""

from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, viewsets

from apps.orders.models import OrderItem
from apps.products.models import Product

from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Відгуки, вкладені під конкретний товар (product_id з URL).

    - GET доступний всім (навіть анонімним).
    - POST лише авторизованим користувачам, які реально купили товар
      (перевірка через OrderItem) і ще не залишали відгук на нього.
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_scope = "reviews"
    http_method_names = ["get", "post", "head", "options"]

    def get_product(self) -> Product:
        return get_object_or_404(Product, pk=self.kwargs["product_id"])

    def get_queryset(self):
        # Під час генерації Swagger-схеми в self.kwargs немає product_id
        # (немає реального запиту з URL) - повертаємо порожній queryset.
        if getattr(self, "swagger_fake_view", False) or "product_id" not in self.kwargs:
            return Review.objects.none()
        return Review.objects.filter(product_id=self.kwargs["product_id"]).select_related("user")

    def perform_create(self, serializer: ReviewSerializer) -> None:
        product = self.get_product()
        user = self.request.user

        has_purchased = OrderItem.objects.filter(order__user=user, product=product).exists()
        if not has_purchased:
            raise serializers.ValidationError(
                "Залишати відгук можна лише після покупки цього товару."
            )

        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("Ви вже залишали відгук на цей товар.")

        serializer.save(product=product, user=user)
