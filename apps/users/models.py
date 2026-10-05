"""Розширення стандартної моделі User через окремий профіль (Profile).

Не наслідуємо AbstractUser, щоб не ускладнювати проєкт - для навчальної
мети зв'язок OneToOne з django.contrib.auth.User достатній і простіший.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Додаткові дані користувача: телефон та адреса за замовчуванням."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField("Телефон", max_length=32, blank=True)
    default_address = models.TextField("Адреса за замовчуванням", blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)

    class Meta:
        verbose_name = "Профіль"
        verbose_name_plural = "Профілі"

    def __str__(self) -> str:
        return f"Профіль {self.user}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs) -> None:
    """Автоматично створює Profile одразу після створення User."""
    if created:
        Profile.objects.create(user=instance)
