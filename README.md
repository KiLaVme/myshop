# Hop & Barley — інтернет-магазин на Django/DRF

> **Стан проєкту: Крок 9/12 — REST API, JWT, документація.**
> Це дев'ятий комміт у покроковій розробці за дорожньою картою з ТЗ.
> Повний функціонал з'являтиметься поступово - див. [CHANGELOG.md](CHANGELOG.md).

Навчальний проєкт: інтернет-магазин товарів для домашнього пивоваріння,
на основі HTML/CSS-шаблону
[Hop & Barley](https://github.com/MagicCodeGit/Hop-and-Barley).

## Що реалізовано на цьому кроці

- Усе з Кроків 1-2 (Docker, uv, PostgreSQL, моделі БД).
- Каталог товарів (`/`, `/products/`): пагінація, пошук за назвою/описом,
  фільтр за категорією та ціною, сортування (новизна/ціна/рейтинг).
- Сторінка товару (`/product/<slug>/`): деталі, рейтинг, відгуки.
  Залишити відгук можна лише після покупки товару (адмінка поки що
  єдиний спосіб увійти/додати замовлення для перевірки - повноцінний
  вхід з'явиться на Кроці 7).
- Кошик (`/cart/`) на основі сесій Django: додавання/зміна кількості/
  видалення товару, перевірка залишків на складі, лічильник у шапці сайту.
- Оформлення замовлення (`/cart/checkout/`): форма контактних даних та
  доставки, атомарне створення замовлення зі списанням складу,
  email-підтвердження (console-backend у DEBUG). Потрібен вхід -
  тепер доступний повноцінний вхід/реєстрація покупців.
- Особистий кабінет (`/account/`): реєстрація, вхід/вихід, історія
  замовлень з фільтром за статусом, редагування профілю, зміна пароля.
- Кастомізована адмін-панель (`/admin/`): зручний список товарів з
  inline-редагуванням, кастомні фільтри та масові дії, сторінка
  "Аналітика продажів" (виторг, середній чек, топ-товари).
- REST API (`/api/`) з JWT-автентифікацією: товари, замовлення, кошик,
  відгуки, реєстрація/логін. Документація: `/api/docs/` (Swagger UI).

## REST API - швидкий приклад

```bash
# Реєстрація (одразу повертає JWT-пару)
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "StrongPass123"}'

# Логін
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "StrongPass123"}'

# Використання access-токена
curl http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

## Швидкий старт

```bash
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py seed_data   # демо-товари
```

Відкрийте http://localhost:8000/ - каталог з демо-товарами.

## Стек технологій

- Python 3.12, Django 5
- PostgreSQL 16
- Docker / Docker Compose, Gunicorn, WhiteNoise
- [uv](https://docs.astral.sh/uv/) — менеджер залежностей та віртуальних оточень

## Запуск (Docker — рекомендовано)

```bash
cp .env.example .env
docker-compose up --build
```

Відкрийте http://localhost:8000/ — побачите заглушку "Hop & Barley",
що підтверджує: Django, PostgreSQL, шаблони та статика працюють коректно.

Адмін-панель: http://localhost:8000/admin/ (суперкористувача поки що
потрібно створити вручну: `docker-compose exec web python manage.py createsuperuser`).

## Локальна розробка з `uv` (без Docker)

```bash
# Встановлення uv (якщо ще не встановлено): https://docs.astral.sh/uv/getting-started/installation/
uv sync                      # створить .venv і встановить залежності з pyproject.toml
uv run python manage.py migrate      # потрібен локальний PostgreSQL (див. .env)
uv run python manage.py runserver
```

`uv sync` читає `pyproject.toml` (і `uv.lock`, якщо він є) та створює
відтворюване оточення `.venv/`. Щоб додати нову залежність:

```bash
uv add <package>          # додає в pyproject.toml і одразу встановлює
uv add --dev <package>    # dev-залежність (лінтери, тести)
uv lock                   # перегенерувати uv.lock після ручних правок pyproject.toml
```

## Структура проєкту (на цьому кроці)

```
myshop/
├── config/
├── apps/
│   ├── products/       # Category, Product + каталог + сторінка товару
│   ├── orders/           # Order, OrderItem (модель, використовується для
│   │                      #   перевірки "чи купував товар")
│   └── reviews/            # Review
├── templates/
│   ├── base.html
│   └── products/
│       ├── catalog.html
│       └── product_detail.html
├── static/
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── pyproject.toml
├── CHANGELOG.md
└── manage.py
```

## CI/CD та підключення до GitHub

CI (`.github/workflows/ci.yml`) працює з Кроку 1. На цьому кроці до
нього додано перевірку валідності OpenAPI-схеми
(`manage.py spectacular --fail-on-warn`) - якщо зміна в серіалізаторі
чи view випадково зламає генерацію схеми, CI одразу це покаже.
Лінтери й тести з'являться на Кроці 10.

Якщо ще не підключали проєкт до GitHub:

```bash
git init && git add . && git commit -m "Крок 9: REST API, JWT, документація"
git branch -M main
git remote add origin https://github.com/<ваш-акаунт>/<repo>.git
git push -u origin main
```

Відкрийте вкладку **Actions** - workflow "CI" запуститься автоматично.

## Наступні кроки

Див. [CHANGELOG.md](CHANGELOG.md). Далі: тести (pytest-django), лінтери (flake8/mypy), типізація.
