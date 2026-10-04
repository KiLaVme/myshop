# Hop & Barley — інтернет-магазин на Django/DRF

> **Стан проєкту: Крок 2/12 — Створення моделей.**
> Це другий комміт у покроковій розробці за дорожньою картою з ТЗ.
> Повний функціонал з'являтиметься поступово - див. [CHANGELOG.md](CHANGELOG.md).

Навчальний проєкт: інтернет-магазин товарів для домашнього пивоваріння,
на основі HTML/CSS-шаблону
[Hop & Barley](https://github.com/MagicCodeGit/Hop-and-Barley).

## Що реалізовано на цьому кроці

- Усе з Кроку 1 (Docker, uv, PostgreSQL, базовий скелет Django).
- Моделі БД: `Category`, `Product`, `Order`, `OrderItem`, `Review`.
- Базова реєстрація моделей в адмін-панелі Django (CRUD "з коробки").

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
├── config/            # settings.py, urls.py, wsgi.py, asgi.py
├── apps/
│   ├── products/       # Category, Product (моделі + базова admin)
│   ├── orders/          # Order, OrderItem (моделі + базова admin)
│   └── reviews/          # Review (модель + базова admin)
├── templates/          # base.html + тимчасова заглушка
├── static/              # CSS/JS/зображення з оригінального шаблону
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── pyproject.toml      # залежності (uv)
├── CHANGELOG.md
└── manage.py
```

## CI/CD та підключення до GitHub

Проєкт має робочий CI з найпершого кроку: `.github/workflows/ci.yml`
(GitHub Actions). Наразі (Крок 2) пайплайн лише
піднімає PostgreSQL, встановлює залежності через `uv sync` і перевіряє, що проєкт застосовує міграції та проходить `manage.py check`. Він розширюватиметься на Кроці 9 (валідація OpenAPI-схеми) та Кроці 10 (flake8, mypy, pytest) - див. [CHANGELOG.md](CHANGELOG.md).

GitHub Actions вмикається автоматично, щойно workflow-файл опиняється в
гілці репозиторію - жодних додаткових налаштувань на боці GitHub не
потрібно.

Відкрийте вкладку **Actions** у репозиторії на GitHub - workflow "CI"
запуститься автоматично на цей push і на кожен наступний push/PR.

## Наступні кроки

Див. [CHANGELOG.md](CHANGELOG.md). Далі: реалізація каталогу товарів
(список, фільтри, пошук, пагінація) на `/` та `/products/`.
