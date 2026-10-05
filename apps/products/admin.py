"""Адмінка додатку products: Category, Product (Крок 8 - кастомізація)."""

from __future__ import annotations

from django.contrib import admin
from django.db.models import QuerySet
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.action(description="Позначити вибрані товари як активні")
def make_active(modeladmin, request, queryset: QuerySet[Product]) -> None:
    """Кастомна дія: масово активувати товари."""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"Активовано товарів: {updated}")


@admin.action(description="Позначити вибрані товари як неактивні")
def make_inactive(modeladmin, request, queryset: QuerySet[Product]) -> None:
    """Кастомна дія: масово деактивувати товари (приховати з каталогу)."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"Деактивовано товарів: {updated}")


class StockLevelFilter(admin.SimpleListFilter):
    """Кастомний фільтр адмінки: рівень залишків на складі."""

    title = "Рівень залишків"
    parameter_name = "stock_level"

    def lookups(self, request, model_admin):
        return [
            ("out", "Немає в наявності (0)"),
            ("low", "Мало (1-5)"),
            ("ok", "Достатньо (>5)"),
        ]

    def queryset(self, request, queryset: QuerySet[Product]) -> QuerySet[Product]:
        if self.value() == "out":
            return queryset.filter(stock=0)
        if self.value() == "low":
            return queryset.filter(stock__gte=1, stock__lte=5)
        if self.value() == "ok":
            return queryset.filter(stock__gt=5)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "image_preview")
    list_filter = ("is_active", "category", StockLevelFilter)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "stock", "is_active")
    actions = [make_active, make_inactive]
    autocomplete_fields = ["category"]

    @admin.display(description="Фото")
    def image_preview(self, obj: Product):
        """Мініатюра зображення товару прямо у списку адмінки."""
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url)
        return "-"
