# Hop & Barley — інтернет-магазин на Django/DRF

> **Стан проєкту: Крок 12/12 — Фінальна версія.**
>Повна історія розробки - у [CHANGELOG.md](CHANGELOG.md),
> чек-лист відповідності ТЗ - у [CHECKLIST.md](CHECKLIST.md).

Навчальний проєкт: інтернет-магазин товарів для домашнього пивоваріння,
реалізований за технічним завданням на основі HTML/CSS-шаблону
[Hop & Barley](https://github.com/MagicCodeGit/Hop-and-Barley).

![CI](https://github.com/kilavme/myshop/actions/workflows/ci.yml/badge.svg)


## Опис проєкту

- **Веб-інтерфейс** на Django (шаблони, сесійна автентифікація):
  каталог, сторінка товару з відгуками, кошик, оформлення замовлення,
  особистий кабінет, адмін-панель з аналітикою.
- **REST API** на DRF з JWT-автентифікацією (access + refresh) для
  зовнішніх клієнтів, документація Swagger/ReDoc.
- **GraphQL** (`/graphql/`) - аналітичні запити для персоналу: виторг,
  тренди продажів, топ-товари, залишки на складі, активність користувачів.
- **CI/CD** (GitHub Actions) - лінт, типізація, тести на кожен push/PR.
- **PostgreSQL** як база даних, **Docker Compose** для розгортання,
  **uv** як менеджер залежностей.

## Стек технологій

- Python 3.12, Django 5, Django REST Framework
- djangorestframework-simplejwt (JWT), django-filter, drf-spectacular,
  graphene-django (GraphQL)
- PostgreSQL 16, Docker / Docker Compose, Gunicorn, WhiteNoise
- [uv](https://docs.astral.sh/uv/) - менеджер залежностей
- pytest-django, flake8, mypy, GitHub Actions

## Структура проєкту

```
myshop/
├── config/                  # Налаштування Django, urls, wsgi/asgi
│   ├── settings.py
│   ├── urls.py                # веб-маршрути + /api/, /api/docs/, /graphql/
│   └── api_urls.py            # усі REST-маршрути /api/...
├── apps/
│   ├── products/               # Category, Product, каталог, фільтри, API
│   ├── orders/                  # Cart (сесія), Order/OrderItem, checkout, API
│   ├── users/                    # Profile, реєстрація/логін, кабінет, API
│   ├── reviews/                    # Review (рейтинги 1-5), API
│   └── graphql/                     # GraphQL-схема аналітики (бонус)
├── templates/                       # Django-шаблони (дизайн Hop & Barley)
├── static/                           # CSS/JS/зображення з оригінального шаблону
├── tests/                             # pytest-тести
├── .github/workflows/ci.yml            # CI (GitHub Actions)
├── docker-compose.yml
├── Dockerfile                          # multi-stage, на основі uv
├── entrypoint.sh
├── pyproject.toml                      # залежності (uv)
├── pytest.ini / setup.cfg / mypy.ini
├── CHANGELOG.md                        # покрокова історія розробки
├── CHECKLIST.md
└── manage.py
```

## Встановлення та запуск (Docker — рекомендовано)

1. Скопіюйте приклад файлу оточення та за потреби відредагуйте:

   ```bash
   cp .env.example .env
   ```

2. Запустіть застосунок та базу даних:

   ```bash
   docker-compose up --build
   ```

   При старті контейнера `web` автоматично: очікується готовність БД,
   генеруються та застосовуються міграції, збирається статика,
   опційно створюється суперкористувач (якщо в `.env` задані
   `DJANGO_SUPERUSER_*`).

3. (Опційно) наповніть каталог демо-товарами:

   ```bash
   docker-compose exec web python manage.py seed_data
   ```

4. Відкрийте:
   - Веб-магазин: http://localhost:8000/
   - Адмін-панель: http://localhost:8000/admin/
   - Swagger API-документація: http://localhost:8000/api/docs/
   - GraphiQL (потрібен вхід як `is_staff`): http://localhost:8000/graphql/

> Контейнер `web` навмисно працює від root (без non-root-користувача) -
> спрощення для навчального проєкту, щоб уникнути конфліктів прав
> доступу з Docker-томами (`static_volume`, `media_volume`) на
> Windows/Docker Desktop.

## Локальна розробка з `uv` (без Docker)

```bash
uv sync --extra dev            # створить .venv і встановить усі залежності
cp .env.example .env           # відредагуйте DB_HOST=localhost тощо
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_data
uv run python manage.py runserver
```

Керування залежностями:

```bash
uv add <package>          # нова залежність (одразу в pyproject.toml)
uv add --dev <package>    # dev-залежність (лінтери, тести)
uv lock                   # перегенерувати uv.lock
uv sync --extra dev       # синхронізувати .venv з pyproject.toml/uv.lock
```

## Тести та лінтери

```bash
docker-compose exec web pytest
docker-compose exec web pytest --cov=apps --cov-report=term-missing
docker-compose exec web flake8 .
docker-compose exec web mypy .
```

Локально (без Docker): замініть `docker-compose exec web` на `uv run`.

Тести покривають: кошик (обмеження за залишками), checkout
(транзакційне створення замовлення, списання складу), доступ до
відгуків лише після покупки, каталог (пошук/фільтри), REST API
(товари, JWT реєстрація/логін, ізоляція замовлень між користувачами),
GraphQL-аналітику (доступ лише для персоналу).

## CI/CD та підключення до GitHub

CI заведений з Кроку 1 і розвивався поступово разом із проєктом:
базова перевірка (міграції + `manage.py check`) → валідація
OpenAPI-схеми (Крок 9) → повний набір `flake8`/`mypy`/`pytest`
(Крок 10). Фінальний `.github/workflows/ci.yml` виконує все це разом.
GitHub Actions вмикається автоматично, щойно файл опиняється в гілці
репозиторію. Після пушу відкрийте вкладку **Actions** у репозиторії - workflow "CI"
запуститься автоматично і надалі виконуватиметься на кожен push у `main`.

## REST API

Базовий URL: `/api/`. Інтерактивна документація - `/api/docs/`
(Swagger UI) або `/api/redoc/` (ReDoc), схема OpenAPI - `/api/schema/`.

### Автентифікація (JWT)

Веб-інтерфейс використовує **сесійну** автентифікацію Django. Для
зовнішніх клієнтів API використовується **JWT** (access + refresh).

```bash
# Реєстрація (одразу повертає JWT-пару)
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "StrongPass123"}'

# Логін
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "StrongPass123"}'
# -> {"access": "...", "refresh": "..."}

# Використання access-токена
curl http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer <access_token>"

# Оновлення access-токена через refresh
curl -X POST http://localhost:8000/api/users/login/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

`access` живе 15 хв (`ACCESS_TOKEN_LIFETIME_MIN`), `refresh` - 7 днів
(`REFRESH_TOKEN_LIFETIME_DAYS`), ротується при кожному оновленні
(`ROTATE_REFRESH_TOKENS=True`).

### Основні ендпоінти

| Ресурс | Дія | URL | Метод |
|---|---|---|---|
| Товари | Список / деталі | `/api/products/`, `/api/products/<id>/` | GET |
| Замовлення | Список своїх / створення з кошика | `/api/orders/` | GET / POST |
| Замовлення | Деталі / скасування | `/api/orders/<id>/` | GET / PATCH |
| Кошик | Перегляд / додати | `/api/cart/` | GET / POST |
| Кошик | Змінити / видалити позицію | `/api/cart/<product_id>/` | PATCH / DELETE |
| Відгуки | Список / додати | `/api/products/<id>/reviews/` | GET / POST |
| Користувачі | Реєстрація / логін / поточний | `/api/users/register\|login\|me/` | POST / POST / GET |

Права доступу: користувач бачить і може змінювати **лише свої**
замовлення та відгуки. Фільтрація/пошук товарів:
`?category=<slug>&min_price=&max_price=&search=&ordering=`.

## GraphQL-аналітика (бонус)

Єдиний ендпоінт `/graphql/` (у DEBUG - інтерактивний GraphiQL UI).
Доступ лише для персоналу (`is_staff=True`), автентифікація через
сесію Django.

```graphql
{
  revenueSummary { totalRevenue ordersCount averageCheck }
  revenueByDate(days: 30) { date revenue ordersCount }
  topProducts(limit: 5) { productName totalQuantity totalRevenue }
  lowStockProducts(threshold: 5) { name stock }
  userActivity(limit: 5) { username ordersCount totalSpent isRepeatCustomer }
}
```

## Веб-функціонал

- **Каталог** (`/`, `/products/`): пагінація, фільтр за категорією та
  ціною, пошук, сортування (новизна/ціна/рейтинг).
- **Сторінка товару** (`/product/<slug>/`): опис, ціна, рейтинг,
  відгуки (лише після покупки - перевірка через `OrderItem`).
- **Кошик** (`/cart/`): сесія Django, перевірка залишків на складі.
- **Оформлення замовлення** (`/cart/checkout/`): форма доставки,
  атомарне створення замовлення (`transaction.atomic`), списання
  складу, email-сповіщення (console-backend у DEBUG).
- **Особистий кабінет** (`/account/`): реєстрація, вхід, історія
  замовлень з фільтром, редагування профілю, зміна пароля.
- **Адмін-панель** (`/admin/`): кастомні дії, фільтри, inline-
  редагування, сторінка "Аналітика продажів" (виторг, середній чек,
  топ-10 товарів).

## Модель даних

`Category` (з вкладеністю через `parent`), `Product`, `Order`/
`OrderItem` (зі снепшотом ціни на момент покупки), `Review`
(унікальний на пару користувач+товар, рейтинг 1-5), `Profile`
(розширення `User`).

## Відомі обмеження

- Оплата в checkout - вибір способу (картка/накладений платіж) без
  реальної інтеграції з платіжним провайдером (за межами ТЗ).
- `mypy` у CI запускається в неблокуючому режимі (`|| true`) - зручно
  для навчального проєкту; прибрати цей прапорець у
  `.github/workflows/ci.yml`, щоб зробити перевірку типів обов'язковою.
