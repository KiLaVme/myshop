"""Серіалізатор відгуків для REST API."""

from __future__ import annotations

from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Серіалізатор відгуку. user проставляється автоматично з request.user."""

    user: serializers.Field = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at"]
        read_only_fields = ["id", "product", "user", "created_at"]
