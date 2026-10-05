"""Email-сповіщення про нове замовлення (клієнту та адміністратору)."""

from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

from .models import Order


def send_order_confirmation_emails(order: Order) -> None:
    """Надсилає лист-підтвердження клієнту і сповіщення адміністратору.

    У DEBUG-режимі за замовчуванням використовується console EmailBackend,
    тож листи просто виводяться в лог контейнера web - зручно для перевірки
    без реального поштового сервера.
    """
    items_lines = "\n".join(
        f"- {item.product.name} x {item.quantity} = {item.total} грн"
        for item in order.items.all()
    )

    customer_message = (
        f"Дякуємо за замовлення #{order.pk}!\n\n"
        f"Товари:\n{items_lines}\n\n"
        f"Загальна сума: {order.total_price} грн\n"
        f"Адреса доставки: {order.shipping_address}\n"
        f"Спосіб оплати: {order.get_payment_method_display()}\n\n"
        "Ми повідомимо вас про зміну статусу замовлення."
    )
    send_mail(
        subject=f"Hop & Barley - підтвердження замовлення #{order.pk}",
        message=customer_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=True,
    )

    admin_message = (
        f"Нове замовлення #{order.pk} від {order.full_name} ({order.email}, {order.phone}).\n\n"
        f"Товари:\n{items_lines}\n\n"
        f"Сума: {order.total_price} грн\n"
        f"Адреса: {order.shipping_address}"
    )
    send_mail(
        subject=f"[Нове замовлення] #{order.pk}",
        message=admin_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )
