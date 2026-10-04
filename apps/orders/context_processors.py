"""Контекст-процесор, що додає кошик в контекст усіх шаблонів.

Завдяки цьому в будь-якому шаблоні доступна змінна {{ cart }},
наприклад для показу кількості товарів у кошику в шапці сайту.
"""

from django.http import HttpRequest

from .cart import Cart


def cart(request: HttpRequest) -> dict:
    """Повертає екземпляр Cart для поточного запиту."""
    return {"cart": Cart(request)}
