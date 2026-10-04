"""
Головний URLConf проєкту.

КРОК 3: `/` та `/products/` тепер ведуть на справжній каталог товарів
(apps.products). Заглушку home_placeholder.html прибрано.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.products.urls", namespace="products")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
