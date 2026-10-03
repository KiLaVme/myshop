# Changelog

Історія розробки проєкту за кроками дорожньої карти з ТЗ (розділ 11).
Кожен крок відповідає окремому коміту.

## Крок 1 — Ініціалізація проєкту

- Налаштовано менеджер залежностей **uv** (`pyproject.toml`).
- Multi-stage `Dockerfile` (builder на `uv` + мінімальний runner-образ).
- `docker-compose.yml`: сервіси `web` + `db` (PostgreSQL 16), у
  розширеному стилі - іменована мережа `hopbarley_network`,
  healthcheck для обох сервісів, іменовані volumes, усі порти
  налаштовуються через `.env` (`DB_EXTERNAL_PORT`, `WEB_EXTERNAL_PORT`).
  Цей файл створюється один раз на Кроці 1 і далі не змінюється.
- `entrypoint.sh`: очікування БД, `makemigrations`/`migrate`, `collectstatic`.
- Базовий скелет Django-проєкту (`config/`: settings/urls/wsgi/asgi).
- Підключено шаблони (`templates/base.html`) та статику (`static/`,
  скопійована з оригінального HTML-дизайну Hop & Barley) - перевірено
  тимчасовою заглушкою на `/`.
- **CI/CD**: базовий `.github/workflows/ci.yml` (GitHub Actions) -
  навмисно заведений одразу на першому кроці, а не "під кінець для
  галочки". Перевіряє встановлення залежностей (`uv sync`),
  застосування міграцій та `manage.py check` на кожен push/PR.
  Розширюватиметься на Кроках 9-10 (валідація API-схеми, лінтери,
  тести).
