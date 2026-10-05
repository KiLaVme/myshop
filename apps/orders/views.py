"""View-класи кошика та оформлення замовлення (веб-інтерфейс)."""

from __future__ import annotations

from typing import cast
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from apps.products.models import Product

from .cart import Cart
from .emails import send_order_confirmation_emails
from .forms import CartAddProductForm, CheckoutForm
from .models import OrderItem


class CartView(TemplateView):
    """Сторінка /cart/ - перегляд вмісту кошика."""

    template_name = "orders/cart.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context


class CartAddView(View):
    """POST /cart/add/<product_id>/ - додати товар у кошик."""

    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, is_active=True)
        form = CartAddProductForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            if not product.in_stock:
                messages.error(request, f'Товару "{product.name}" немає в наявності.')
            else:
                cart.add(product=product, quantity=cd["quantity"], override_quantity=cd["override"])
                messages.success(request, f'Товар "{product.name}" додано в кошик.')
        else:
            messages.error(request, "Некоректна кількість товару.")

        next_url = request.POST.get("next") or reverse_lazy("orders:cart_detail")
        return redirect(next_url)


class CartRemoveView(View):
    """POST /cart/remove/<product_id>/ - видалити товар з кошика."""

    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        messages.info(request, f'Товар "{product.name}" видалено з кошика.')
        return redirect("orders:cart_detail")


class CheckoutView(LoginRequiredMixin, FormView):
    """Сторінка /cart/checkout/ - оформлення замовлення.

    Доступна лише авторизованим користувачам (LoginRequiredMixin),
    щоб замовлення завжди було прив'язане до конкретного акаунту.
    Повноцінний веб-логін для покупців з'явиться на Кроці 7 - до того
    часу для входу можна користуватись стандартною адмін-панеллю
    Django (`/admin/login/`), яка вже доступна за замовчуванням.
    """

    template_name = "orders/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("orders:checkout_success")

    def get_initial(self) -> dict:
        user = cast(User, self.request.user)
        return {
            "full_name": user.get_full_name() or user.username,
            "email": user.email,
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart(self.request)
        return context

    def dispatch(self, request, *args, **kwargs):
        cart = Cart(request)
        if len(cart) == 0 and request.method == "GET":
            messages.warning(request, "Ваш кошик порожній.")
            return redirect("orders:cart_detail")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: CheckoutForm) -> HttpResponse:
        cart = Cart(self.request)

        if len(cart) == 0:
            messages.error(self.request, "Ваш кошик порожній.")
            return redirect("orders:cart_detail")

        if cart.has_stock_issues():
            messages.error(
                self.request,
                "У кошику є товари, кількість яких перевищує наявний залишок на складі.",
            )
            return redirect("orders:cart_detail")

        # Створення замовлення виконуємо атомарно: або все успішно
        # (замовлення + позиції + списання залишків), або нічого.
        with transaction.atomic():
            order = form.save(commit=False)
            order.user = cast(User, self.request.user)
            order.save()

            for item in cart:
                product = item["product"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    price=item["price"],
                )
                product.stock -= item["quantity"]
                product.save(update_fields=["stock"])

            order.recalculate_total()

        send_order_confirmation_emails(order)
        cart.clear()

        self.request.session["last_order_id"] = order.id
        return super().form_valid(form)


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    """Сторінка подяки після успішного оформлення замовлення."""

    template_name = "orders/checkout_success.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get("last_order_id")
        user = cast(User, self.request.user)
        context["order"] = (
            user.orders.filter(id=order_id).first() if order_id else None
        )
        return context
