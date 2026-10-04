"""URL-маршрути додатку products (каталог).

Сторінка товару (`product/<slug>/`) додасться на Кроці 4.
"""

from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="catalog"),
    path("products/", views.ProductListView.as_view(), name="catalog_alt"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
