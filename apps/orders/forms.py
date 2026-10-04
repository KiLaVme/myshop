"""Форми для кошика (форма оформлення замовлення з'явиться на Кроці 6)."""

from __future__ import annotations

from django import forms


class CartAddProductForm(forms.Form):
    """Форма вибору кількості на сторінці товару / кошика."""

    quantity = forms.IntegerField(min_value=1, initial=1, label="Кількість")
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
