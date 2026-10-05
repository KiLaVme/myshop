"""Адмінка додатку orders: Order, OrderItem + аналітична сторінка (Крок 8).

Аналітика (виторг, топ-товари, кількість замовлень) реалізована через
django.db.models агрегації/анотації та кастомний admin-view,
доступний за посиланням "Аналітика продажів" у списку замовлень.
"""

from __future__ import annotations

from django.contrib import admin
from django.db.models import Count, Sum, F
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Позиції замовлення редагуються прямо всередині Order."""

    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")
    can_delete = False


@admin.action(description="Позначити як оплачені")
def mark_paid(modeladmin, request, queryset):
    updated = queryset.update(status=Order.Status.PAID)
    modeladmin.message_user(request, f"Оновлено замовлень: {updated}")


@admin.action(description="Позначити як відправлені")
def mark_shipped(modeladmin, request, queryset):
    updated = queryset.update(status=Order.Status.SHIPPED)
    modeladmin.message_user(request, f"Оновлено замовлень: {updated}")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "user__username", "user__email", "full_name", "email")
    inlines = [OrderItemInline]
    actions = [mark_paid, mark_shipped]
    date_hierarchy = "created_at"
    change_list_template = "admin/orders/order_changelist.html"

    def get_urls(self):
        """Додає власний URL /admin/orders/order/analytics/ з аналітичною сторінкою."""
        urls = super().get_urls()
        custom = [
            path("analytics/", self.admin_site.admin_view(self.analytics_view), name="orders_analytics"),
        ]
        return custom + urls

    def analytics_view(self, request):
        """Проста сторінка аналітики: виторг, кількість замовлень, топ-товари."""
        orders_qs = Order.objects.exclude(status=Order.Status.CANCELLED)

        summary = orders_qs.aggregate(
            total_revenue=Sum("total_price"),
            orders_count=Count("id"),
        )
        avg_check = (
            (summary["total_revenue"] / summary["orders_count"])
            if summary["orders_count"]
            else 0
        )

        top_products = (
            OrderItem.objects.filter(order__in=orders_qs)
            .values("product__name")
            .annotate(
                total_quantity=Sum("quantity"),
                total_revenue=Sum(F("price") * F("quantity")),
            )
            .order_by("-total_quantity")[:10]
        )

        context = dict(
            self.admin_site.each_context(request),
            title="Аналітика продажів",
            total_revenue=summary["total_revenue"] or 0,
            orders_count=summary["orders_count"] or 0,
            avg_check=avg_check,
            top_products=top_products,
            generated_at=timezone.now(),
        )
        return render(request, "admin/orders/analytics.html", context)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")
    search_fields = ("order__id", "product__name")
