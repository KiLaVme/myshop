"""Форми для кошика та оформлення замовлення."""

from __future__ import annotations

from django import forms

from .models import Order


class CartAddProductForm(forms.Form):
    """Форма вибору кількості на сторінці товару / кошика."""

    quantity = forms.IntegerField(min_value=1, initial=1, label="Кількість")
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class CheckoutForm(forms.ModelForm):
    """Форма контактних даних, адреси доставки та способу оплати."""

    class Meta:
        model = Order
        fields = ["full_name", "email", "phone", "shipping_address", "payment_method"]
        widgets = {
            "shipping_address": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_phone(self) -> str:
        """Проста валідація телефону - тільки цифри, +, пробіли та дужки."""
        phone = self.cleaned_data["phone"]
        cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not cleaned.replace("+", "").isdigit():
            raise forms.ValidationError("Введіть коректний номер телефону.")
        return phone
