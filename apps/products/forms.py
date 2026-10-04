"""Форми додатку products."""

from __future__ import annotations

from django import forms

from apps.reviews.models import Review


class ReviewForm(forms.ModelForm):
    """Форма залишення відгуку на товар."""

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} ★") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Ваш відгук..."}),
        }
