"""
Головний URLConf проєкту.

КРОК 1: поки що тут лише адмінка та тимчасова сторінка-заглушка на `/`,
яка підтверджує, що шаблони (templates/) та статика (static/) підключені
й коректно рендеряться. У наступних кроках `/` заміниться на справжній
каталог товарів (apps.products), а список маршрутів розшириться
(cart/, checkout/, account/, api/, graphql/ тощо).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home_placeholder.html"), name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
