# ══════════════════════════════════════════════════════════
# Dockerfile для Django-бекенду Hop & Barley Shop
# Multi-stage build: окрема збірка залежностей (uv) і мінімальний
# фінальний образ без інструментів збірки.
# ══════════════════════════════════════════════════════════

# ──────────────────────────────────────────────
# STAGE 1: builder — встановлення залежностей через uv
# ──────────────────────────────────────────────
# Повний slim-образ, у якому ставимо uv та залежності проєкту
FROM python:3.12-slim AS builder

# Встановлюємо робочу директорію для збірки
WORKDIR /build

# uv - сучасний, значно швидший за pip менеджер залежностей Python
RUN pip install --no-cache-dir uv

# Копіюємо лише файл залежностей першим —
# Docker кешує цей шар, якщо pyproject.toml не змінився
COPY pyproject.toml ./

# Створюємо ізольоване venv-оточення та встановлюємо в нього залежності
# з pyproject.toml. Саме venv (а не --target) обрано свідомо: так у venv
# коректно потрапляють і "console scripts" (наприклад, бінарник gunicorn),
# а не лише імпортовані пакети.
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --no-cache -r pyproject.toml


# ──────────────────────────────────────────────
# STAGE 2: runner — фінальний мінімальний образ
# ──────────────────────────────────────────────
# Знову slim-образ — без uv та зайвих інструментів збірки
FROM python:3.12-slim AS runner

# Метадані образу
LABEL maintainer="hop-and-barley-shop"
LABEL description="Django backend for the Hop & Barley online shop"
LABEL version="1.0"

# Встановлюємо робочу директорію застосунку
WORKDIR /app

# ── Копіюємо готове venv-оточення зі stage builder ─────
# Тільки встановлені пакети - без uv, pip-кешу тощо
COPY --from=builder /opt/venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ── Копіюємо код застосунку ───────────────────
COPY manage.py .
COPY config/ ./config/
COPY apps/ ./apps/
COPY templates/ ./templates/
COPY static/ ./static/
COPY entrypoint.sh .

# ── Створення необхідних директорій ───────────
# Будуть перезаписані volume-ами з docker-compose, але створюємо
# на випадок запуску образу без compose
RUN mkdir -p /app/staticfiles /app/media

# ── Налаштування середовища ───────────────────
# Забороняємо Python буферизувати stdout/stderr
# (логи з'являються одразу, без затримок, зручно для docker-compose logs)
ENV PYTHONUNBUFFERED=1

# Python не створює .pyc файли (зменшує розмір, не потрібно в контейнері)
ENV PYTHONDONTWRITEBYTECODE=1

# ── Відкриваємо порт ───────────────────────────
# Django/gunicorn слухає на порту 8000
EXPOSE 8000

# entrypoint.sh чекає на БД, генерує/застосовує міграції, збирає статику
ENTRYPOINT ["/app/entrypoint.sh"]

# ── Команда запуску ────────────────────────────
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
