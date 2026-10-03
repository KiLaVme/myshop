# Hop & Barley — інтернет-магазин на Django/DRF

> **Стан проєкту: Крок 1/12 — Ініціалізація.**
> Це перший комміт у покроковій розробці за дорожньою картою з ТЗ.
> Повний функціонал з'являтиметься поступово - див. [CHANGELOG.md](CHANGELOG.md).

Навчальний проєкт: інтернет-магазин товарів для домашнього пивоваріння,
на основі HTML/CSS-шаблону
[Hop & Barley](https://github.com/MagicCodeGit/Hop-and-Barley).

## Що реалізовано на цьому кроці

- Docker + Docker Compose (застосунок + PostgreSQL 16).
- Менеджер залежностей **uv** (`pyproject.toml`) замість `requirements.txt`.
- Базовий скелет Django-проєкту.
- Підключення шаблонів (`templates/`) та статики (`static/`).

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
├── apps/              # (порожньо - додатки з'являться з Кроку 2)
├── templates/          # base.html + тимчасова заглушка
├── static/             # CSS/JS/зображення з оригінального шаблону
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── pyproject.toml      # залежності (uv)
├── CHANGELOG.md
└── manage.py
```

## CI/CD та підключення до GitHub

Проєкт має робочий CI з найпершого кроку: `.github/workflows/ci.yml`
(GitHub Actions). Наразі (Крок 1) пайплайн лише
піднімає PostgreSQL, встановлює залежності через `uv sync` і перевіряє,
що проєкт застосовує міграції та проходить `manage.py check`. Він
розширюватиметься на Кроці 9 (валідація OpenAPI-схеми) та Кроці 10
(flake8, mypy, pytest) - див. [CHANGELOG.md](CHANGELOG.md).

GitHub Actions вмикається автоматично, щойно workflow-файл опиняється в
гілці репозиторію - жодних додаткових налаштувань на боці GitHub не
потрібно.

Відкрийте вкладку **Actions** у репозиторії на GitHub - workflow "CI"
запуститься автоматично.

## Наступні кроки

Див. [CHANGELOG.md](CHANGELOG.md) та дорожню карту в ТЗ. Далі: моделі
`Category`/`Product`/`Order`/`OrderItem`/`Review`, потім каталог товарів.
