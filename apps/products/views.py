"""View-класи каталогу товарів (веб-інтерфейс).

Крок 3 - список товарів. Крок 4 додає детальну сторінку товару з
відгуками (форма відгуку доступна лише авторизованим користувачам,
які реально купили товар - перевірка через apps.orders.models.OrderItem).
"""

from __future__ import annotations

from django.contrib import messages
from django.db.models import Q, QuerySet
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin

from apps.orders.models import OrderItem
from apps.reviews.models import Review

from .filters import ProductFilter
from .forms import ReviewForm
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


class ProductDetailView(FormMixin, DetailView):
    """Сторінка `/product/<slug>/` - деталі товару, відгуки, форма відгуку.

    Кнопка "Додати в кошик" з'явиться на Кроці 5 разом із реалізацією
    кошика (зараз показуємо лише вибір кількості як прев'ю UI).
    """

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"
    form_class = ReviewForm

    def get_queryset(self) -> QuerySet[Product]:
        return Product.objects.select_related("category").prefetch_related("reviews__user")

    def get_success_url(self) -> str:
        return reverse("products:product_detail", kwargs={"slug": self.object.slug})

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        product = self.object

        context["reviews"] = product.reviews.select_related("user").all()
        ratings = [r.rating for r in context["reviews"]]
        context["avg_rating"] = round(sum(ratings) / len(ratings), 1) if ratings else None

        user = self.request.user
        if user.is_authenticated:
            context["user_has_purchased"] = self._user_has_purchased(user, product)
            context["user_has_reviewed"] = product.reviews.filter(user=user).exists()
        else:
            context["user_has_purchased"] = False
            context["user_has_reviewed"] = False

        context.setdefault("form", self.get_form())
        return context

    @staticmethod
    def _user_has_purchased(user, product: Product) -> bool:
        """Перевіряє, чи користувач купував цей товар (для дозволу залишити відгук)."""
        return OrderItem.objects.filter(order__user=user, product=product).exists()

    def post(self, request, *args, **kwargs):
        """Обробка форми відгуку - лише для авторизованих користувачів, що купили товар."""
        self.object = self.get_object()
        product = self.object

        if not request.user.is_authenticated:
            messages.error(request, "Щоб залишити відгук, увійдіть у свій акаунт.")
            return redirect(self.get_success_url())

        if not self._user_has_purchased(request.user, product):
            messages.error(request, "Залишати відгук можна лише після покупки товару.")
            return redirect(self.get_success_url())

        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, "Ви вже залишали відгук на цей товар.")
            return redirect(self.get_success_url())

        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Дякуємо за ваш відгук!")
            return redirect(self.get_success_url())

        return self.form_invalid(form)
