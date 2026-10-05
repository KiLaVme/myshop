"""REST API view-класи для товарів."""

from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import ProductFilter
from .models import Product
from .serializers import ProductDetailSerializer, ProductListSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/products/ та /api/products/<id>/ - тільки читання.

    Товари створюються/редагуються через Django Admin (адмін-панель),
    а не через публічний API, тому це ReadOnlyModelViewSet.
    """

    queryset = Product.objects.active().select_related("category").with_rating()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "avg_rating"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
