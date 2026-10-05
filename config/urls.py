"""
Головний URLConf проєкту.

КРОК 3: `/` та `/products/` тепер ведуть на справжній каталог товарів
(apps.products). Заглушку home_placeholder.html прибрано.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.products.urls", namespace="products")),
    path("", include("apps.orders.urls", namespace="orders")),
    path("account/", include("apps.users.urls", namespace="users")),

    # REST API
    path("api/", include("config.api_urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
