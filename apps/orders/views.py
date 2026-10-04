"""View-класи кошика (веб-інтерфейс).

Крок 5 дорожньої карти - лише кошик. Оформлення замовлення (checkout)
з'явиться на Кроці 6.
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from apps.products.models import Product

from .cart import Cart
from .forms import CartAddProductForm


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
