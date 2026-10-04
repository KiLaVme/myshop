"""Фільтри каталогу товарів: категорія та діапазон цін.

FilterSet описаний один раз тут і буде повторно використаний у REST API
на Кроці 9 (apps.products.api_views.ProductViewSet).
"""

from __future__ import annotations

import django_filters

from .models import Category, Product


class ProductFilter(django_filters.FilterSet):
    """FilterSet: category (slug), min_price, max_price."""

    category = django_filters.ModelChoiceFilter(
        field_name="category",
        to_field_name="slug",
        queryset=Category.objects.all(),
        label="Категорія",
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price"]
