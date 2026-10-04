"""View-класи каталогу товарів (веб-інтерфейс).

Крок 3 дорожньої карти - лише список товарів. Детальна сторінка товару
з'явиться на Кроці 4.
"""

from __future__ import annotations

from django.db.models import Q, QuerySet
from django.views.generic import ListView

from .filters import ProductFilter
from .models import Category, Product

SORT_OPTIONS = {
    "new": "-created_at",
    "price_asc": "price",
    "price_desc": "-price",
    "rating": "-avg_rating",
}


class ProductListView(ListView):
    """Сторінки `/` та `/products/` - каталог з пошуком, фільтрами, сортуванням, пагінацією."""

    model = Product
    template_name = "products/catalog.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self) -> QuerySet[Product]:
        # select_related("category") - уникаємо N+1 запитів на категорію в шаблоні
        queryset = (
            Product.objects.active()
            .select_related("category")
            .with_rating()
        )

        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        self.product_filter = ProductFilter(self.request.GET, queryset=queryset)
        queryset = self.product_filter.qs

        sort_key = self.request.GET.get("sort", "new")
        queryset = queryset.order_by(SORT_OPTIONS.get(sort_key, SORT_OPTIONS["new"]))

        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["search_query"] = self.request.GET.get("q", "")
        context["current_sort"] = self.request.GET.get("sort", "new")
        context["current_category"] = self.request.GET.get("category", "")
        context["sort_choices"] = [
            ("new", "Новинки"),
            ("price_asc", "Ціна ↑"),
            ("price_desc", "Ціна ↓"),
            ("rating", "Рейтинг"),
        ]
        return context
