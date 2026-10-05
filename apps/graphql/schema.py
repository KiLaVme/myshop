"""GraphQL-схема (бонусне завдання за ТЗ, п. 11).

Єдиний ендпоінт `/graphql/`. Призначення - аналітичні запити для
адміністраторів: виторг/тренди по замовленнях, популярні товари та
залишки на складі, активність користувачів (повторні покупки).

Усі резолвери вимагають автентифікованого staff-користувача
(is_staff=True) - аналітика не є публічними даними.
"""

from __future__ import annotations

import graphene
from django.contrib.auth.models import User
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from apps.orders.models import Order, OrderItem
from apps.products.models import Product


def _require_staff(info: graphene.ResolveInfo) -> None:
    """Допоміжна перевірка: доступ до аналітики лише для персоналу (is_staff)."""
    user = info.context.user
    if not user.is_authenticated or not user.is_staff:
        raise GraphQLError("Доступ до аналітики дозволено лише персоналу магазину.")


class ProductType(DjangoObjectType):
    """GraphQL-тип товару - для запитів про залишки на складі."""

    class Meta:
        model = Product
        fields = ("id", "name", "slug", "price", "stock", "is_active", "category")


class RevenueSummaryType(graphene.ObjectType):
    """Загальна статистика по замовленнях: виторг, кількість, середній чек."""

    total_revenue = graphene.Decimal()
    orders_count = graphene.Int()
    average_check = graphene.Decimal()


class RevenueByDateType(graphene.ObjectType):
    """Точка тренду виторгу по днях."""

    date = graphene.Date()
    revenue = graphene.Decimal()
    orders_count = graphene.Int()


class TopProductType(graphene.ObjectType):
    """Рядок рейтингу популярних товарів."""

    product_name = graphene.String()
    total_quantity = graphene.Int()
    total_revenue = graphene.Decimal()


class UserActivityType(graphene.ObjectType):
    """Активність користувача: кількість замовлень, сума покупок, чи повторний клієнт."""

    username = graphene.String()
    email = graphene.String()
    orders_count = graphene.Int()
    total_spent = graphene.Decimal()
    is_repeat_customer = graphene.Boolean()


class Query(graphene.ObjectType):
    """Кореневий Query-тип GraphQL API магазину."""

    revenue_summary = graphene.Field(
        RevenueSummaryType,
        description="Загальний виторг, кількість замовлень та середній чек (без скасованих).",
    )
    revenue_by_date = graphene.List(
        RevenueByDateType,
        days=graphene.Int(default_value=30),
        description="Тренд виторгу по днях за останні N днів.",
    )
    top_products = graphene.List(
        TopProductType,
        limit=graphene.Int(default_value=10),
        description="Найпопулярніші товари за кількістю проданих одиниць.",
    )
    low_stock_products = graphene.List(
        ProductType,
        threshold=graphene.Int(default_value=5),
        description="Товари, залишок яких на складі не перевищує threshold.",
    )
    user_activity = graphene.List(
        UserActivityType,
        limit=graphene.Int(default_value=10),
        description="Топ активних користувачів за сумою покупок, з ознакою повторних покупок.",
    )

    def resolve_revenue_summary(root, info: graphene.ResolveInfo) -> RevenueSummaryType:
        _require_staff(info)
        orders = Order.objects.exclude(status=Order.Status.CANCELLED)
        agg = orders.aggregate(total_revenue=Sum("total_price"), orders_count=Count("id"))
        total_revenue = agg["total_revenue"] or 0
        orders_count = agg["orders_count"] or 0
        avg_check = (total_revenue / orders_count) if orders_count else 0
        return RevenueSummaryType(
            total_revenue=total_revenue, orders_count=orders_count, average_check=avg_check
        )

    def resolve_revenue_by_date(root, info: graphene.ResolveInfo, days: int):
        _require_staff(info)
        since = timezone.now() - timedelta(days=days)
        rows = (
            Order.objects.exclude(status=Order.Status.CANCELLED)
            .filter(created_at__gte=since)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(revenue=Sum("total_price"), orders_count=Count("id"))
            .order_by("date")
        )
        return [
            RevenueByDateType(date=r["date"], revenue=r["revenue"], orders_count=r["orders_count"])
            for r in rows
        ]

    def resolve_top_products(root, info: graphene.ResolveInfo, limit: int):
        _require_staff(info)
        rows = (
            OrderItem.objects.exclude(order__status=Order.Status.CANCELLED)
            .values("product__name")
            .annotate(total_quantity=Sum("quantity"), total_revenue=Sum(F("price") * F("quantity")))
            .order_by("-total_quantity")[:limit]
        )
        return [
            TopProductType(
                product_name=r["product__name"],
                total_quantity=r["total_quantity"],
                total_revenue=r["total_revenue"],
            )
            for r in rows
        ]

    def resolve_low_stock_products(root, info: graphene.ResolveInfo, threshold: int):
        _require_staff(info)
        return Product.objects.filter(stock__lte=threshold, is_active=True).order_by("stock")

    def resolve_user_activity(root, info: graphene.ResolveInfo, limit: int):
        _require_staff(info)
        rows = (
            User.objects.annotate(
                orders_count=Count("orders"),
                total_spent=Sum("orders__total_price"),
            )
            .filter(orders_count__gt=0)
            .order_by("-total_spent")[:limit]
        )
        return [
            UserActivityType(
                username=u.username,
                email=u.email,
                orders_count=u.orders_count,
                total_spent=u.total_spent or 0,
                is_repeat_customer=u.orders_count > 1,
            )
            for u in rows
        ]


schema = graphene.Schema(query=Query)
