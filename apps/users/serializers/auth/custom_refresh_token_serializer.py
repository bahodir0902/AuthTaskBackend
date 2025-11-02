from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.users.auth.jwt import blacklist_token, decode_jwt_token, is_blacklisted, make_jwt_token
from apps.users.models import User


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh = attrs["refresh"]
            decoded = decode_jwt_token(refresh)
            user_id = decoded.get("user_id")
        except Exception:
            raise AuthenticationFailed("Invalid refresh token")

        if decoded.get("type") != "refresh":
            raise AuthenticationFailed("Token is not a refresh token")

        jti = decoded.get("jti")
        if is_blacklisted(jti):
            raise AuthenticationFailed("Refresh token been revoked")

        user = User.objects.filter(pk=user_id).first()
        if not user:
            raise AuthenticationFailed("User not found")

        if not user.is_active:
            raise AuthenticationFailed("User is disabled")

        if not getattr(user, "email_verified", False):
            raise AuthenticationFailed("Email not verified")

        if getattr(user, "must_set_password", False):
            raise AuthenticationFailed("User must set password")

        data = super().validate(attrs)

        data["payload"] = decoded
        return data

    def create(self, validated_data):
        payload = validated_data["payload"]
        user = User.objects.get(pk=payload["user_id"])

        old_jti = payload.get("jti")
        if getattr(settings, "JWT_REFRESH_ROTATE", True):
            blacklist_token(old_jti, "refresh", user)

        access, _ = make_jwt_token(user, token_type="access")
        refresh, _ = make_jwt_token(user, token_type="refresh")

        return {"access": access, "refresh": refresh}
