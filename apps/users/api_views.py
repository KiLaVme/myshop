"""REST API view-класи для користувачів: реєстрація, JWT-логін, поточний користувач."""

from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, UserSerializer


class RegisterAPIView(generics.CreateAPIView):
    """POST /api/users/register/ - створення акаунту через API."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request: Request, *args, **kwargs) -> Response:
        response = super().create(request, *args, **kwargs)
        # Одразу видаємо JWT-пару, щоб клієнт міг залогінитись без другого запиту
        user = self.get_serializer().Meta.model.objects.get(pk=response.data["id"])
        refresh = RefreshToken.for_user(user)
        response.data["tokens"] = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        return response


class LoginAPIView(TokenObtainPairView):
    """POST /api/users/login/ - отримати access/refresh JWT токени."""


class MeAPIView(APIView):
    """GET /api/users/me/ - дані поточного авторизованого користувача."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer  # лише для коректної генерації Swagger-схеми

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
