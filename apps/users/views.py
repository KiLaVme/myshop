"""View-класи додатку users: реєстрація, кабінет, історія замовлень."""

from __future__ import annotations

from typing import Any, cast
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
    PasswordChangeView as DjangoPasswordChangeView,
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from apps.orders.models import Order

from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from .models import Profile


class RegisterView(CreateView):
    """Сторінка `/account/register/` - реєстрація нового користувача."""

    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:account")

    def form_valid(self, form: RegisterForm):
        response = super().form_valid(form)
        # Одразу логінимо користувача після реєстрації (session-based auth)
        login(self.request, self.object)
        messages.success(self.request, "Реєстрація успішна! Ласкаво просимо.")
        return response


class LoginView(DjangoLoginView):
    """Сторінка `/account/login/` - вхід через сесійну автентифікацію."""

    template_name = "users/login.html"
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    """Вихід користувача (POST /account/logout/)."""

    next_page = reverse_lazy("products:catalog")


class AccountView(LoginRequiredMixin, TemplateView):
    """Особистий кабінет `/account/` - історія замовлень з фільтрацією за статусом."""

    template_name = "users/account.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        user = cast(User, self.request.user)

        orders = Order.objects.filter(user=user).prefetch_related("items__product")

        status = self.request.GET.get("status")
        if status:
            orders = orders.filter(status=status)

        context["orders"] = orders
        context["status_choices"] = Order.Status.choices
        context["current_status"] = status or ""
        return context


class ProfileEditView(LoginRequiredMixin, TemplateView):
    """Редагування профілю: дані користувача + додаткові поля Profile."""

    template_name = "users/profile_edit.html"

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        return self.render_to_response({"user_form": user_form, "profile_form": profile_form})

    def post(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Профіль оновлено.")
            return self.render_to_response(
                {"user_form": user_form, "profile_form": profile_form, "saved": True}
            )

        return self.render_to_response({"user_form": user_form, "profile_form": profile_form})


class PasswordChangeView(LoginRequiredMixin, DjangoPasswordChangeView):
    """Зміна пароля через стандартний Django PasswordChangeForm."""

    template_name = "users/password_change.html"
    success_url = reverse_lazy("users:account")

    def form_valid(self, form):
        messages.success(self.request, "Пароль успішно змінено.")
        return super().form_valid(form)
