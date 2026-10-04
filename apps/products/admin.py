"""Адмінка додатку products (базова реєстрація).

Кастомізація (list_filter, actions, аналітика) з'явиться на Кроці 8.
"""

from django.contrib import admin

from .models import Category, Product

admin.site.register(Category)
admin.site.register(Product)
