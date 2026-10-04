"""Адмінка додатку reviews (базова реєстрація)."""

from django.contrib import admin

from .models import Review

admin.site.register(Review)
