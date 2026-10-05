"""Адмінка додатку users: показуємо Profile inline всередині стандартного UserAdmin."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Профіль"


class UserAdmin(DjangoUserAdmin):
    inlines = (ProfileInline,)
    list_display = DjangoUserAdmin.list_display + ("is_staff", "date_joined")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
