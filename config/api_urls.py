"""Маршрути REST API, зібрані під префіксом /api/."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.orders.api_views import CartAPIView, CartItemAPIView, OrderViewSet
from apps.products.api_views import ProductViewSet
from apps.reviews.api_views import ReviewViewSet
from apps.users.api_views import RegisterAPIView, LoginAPIView, MeAPIView

router = DefaultRouter()
router.register("products", ProductViewSet, basename="api-products")
router.register("orders", OrderViewSet, basename="api-orders")

urlpatterns = [
    path("", include(router.urls)),

    path("users/register/", RegisterAPIView.as_view(), name="api-register"),
    path("users/login/", LoginAPIView.as_view(), name="api-login"),
    path("users/login/refresh/", TokenRefreshView.as_view(), name="api-login-refresh"),
    path("users/me/", MeAPIView.as_view(), name="api-me"),

    path("cart/", CartAPIView.as_view(), name="api-cart"),
    path("cart/<int:product_id>/", CartItemAPIView.as_view(), name="api-cart-item"),

    path(
        "products/<int:product_id>/reviews/",
        ReviewViewSet.as_view({"get": "list", "post": "create"}),
        name="api-product-reviews",
    ),
]
