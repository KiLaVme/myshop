"""
Django settings for the Hop & Barley (myshop) project.

Крок 1 (ініціалізація проєкту): тут налаштовано лише базову
інфраструктуру - Django, PostgreSQL, статика/шаблони. У наступних
кроках цей файл поступово доповнюватиметься (додатки products/orders/
users/reviews, DRF, JWT, GraphQL тощо) - див. CHANGELOG.md.

Усі "секретні" та середовищно-залежні значення читаються зі змінних
оточення (.env файл), щоб один і той самий образ Docker можна було
використовувати і локально, і в проді, просто підмінюючи .env.
"""

from pathlib import Path

from dotenv import load_dotenv
from datetime import timedelta
import os
import sys

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    """Допоміжна функція: перетворює рядкову змінну оточення на bool."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key-please-change")
DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# -----------------------------------------------------------------
# Applications
# -----------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # Сторонні бібліотеки
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",

    # Додатки проєкту
    "apps.products",
    "apps.orders",
    "apps.reviews",
    "apps.users",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.orders.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# -----------------------------------------------------------------
# Database - PostgreSQL (обов'язково за ТЗ, з першого ж кроку)
# -----------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "hopbarley"),
        "USER": os.environ.get("DB_USER", "hopbarley_user"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "hopbarley_pass"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

# -----------------------------------------------------------------
# Password validation
# -----------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------
# Internationalization
# -----------------------------------------------------------------
LANGUAGE_CODE = "uk"
TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------
# Перевіряємо, чи запущено виконання тестів
# -----------------------------------------------------------------
TESTING = "pytest" in sys.modules or "test" in sys.argv

# -----------------------------------------------------------------
# Static & media files
# -----------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        # Під час тестів використовуємо звичайне StaticFilesStorage,
        # щоб не вимагати наявності згенерованого staticfiles.json
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------------------------------------------
# Кошик - назва ключа сесії
# -----------------------------------------------------------------
CART_SESSION_ID = "cart"

# -----------------------------------------------------------------
# Авторизація / сесії (веб-інтерфейс - session-based)
# -----------------------------------------------------------------
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:account"
LOGOUT_REDIRECT_URL = "products:catalog"

# -----------------------------------------------------------------
# Пошта
# -----------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@hopandbarley.local")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@hopandbarley.local")

# -----------------------------------------------------------------
# Django REST Framework
# -----------------------------------------------------------------
REST_FRAMEWORK = {
    # За замовчуванням API вимагає JWT (для зовнішніх клієнтів),
    # а SessionAuthentication дозволяє користуватись і Swagger UI
    # залогінившись через звичайну Django-сесію (адмінка/браузер).
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "reviews": "20/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_LIFETIME_MIN", 15))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("REFRESH_TOKEN_LIFETIME_DAYS", 7))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Hop & Barley Shop API",
    "DESCRIPTION": (
        "REST API інтернет-магазину товарів для пивоваріння. "
        "Веб-інтерфейс використовує сесійну автентифікацію, "
        "цей API - JWT (access + refresh)."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# -----------------------------------------------------------------
# CORS (щоб зовнішні SPA-клієнти могли звертатись до /api/)
# -----------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

# -----------------------------------------------------------------
# Логування - виводимо все у консоль (зручно для docker-compose logs)
# -----------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
