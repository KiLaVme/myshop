"""URL-маршрути додатку users (акаунт, автентифікація)."""

from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.AccountView.as_view(), name="account"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("password/", views.PasswordChangeView.as_view(), name="password_change"),
]
