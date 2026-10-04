"""Адмінка додатку orders (базова реєстрація).

Кастомізація та сторінка аналітики продажів з'являться на Кроці 8.
"""

from django.contrib import admin

from .models import Order, OrderItem

admin.site.register(Order)
admin.site.register(OrderItem)
