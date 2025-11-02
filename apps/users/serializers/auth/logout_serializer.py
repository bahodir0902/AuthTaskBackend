import logging

from rest_framework import serializers

from apps.users.auth.jwt import blacklist_token, decode_jwt_token
from apps.users.models import User

logger = logging.getLogger(__name__)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")
        if not refresh_token:
            logger.warning("users.logout. User did not provide refresh token")
            raise serializers.ValidationError("refresh_token is required")

        try:
            token_payload = decode_jwt_token(token=refresh_token)
        except Exception as e:
            logger.warning("users.logout. Invalid refresh token: %s", e)
            raise serializers.ValidationError("Invalid refresh token")

        request_user_id = self.context["request"].user.pk
        token_user_id = token_payload.get("user_id")

        user = User.objects.filter(pk=token_user_id).first()

        if not user:
            raise serializers.ValidationError("User does not exist")

        if token_user_id and request_user_id and (str(token_user_id) != str(request_user_id)):
            logger.warning(
                "users.logout. Refresh token does not belong to user id=%s", request_user_id
            )
            raise serializers.ValidationError("This refresh token does not belong to you")

        jti = token_payload.get("jti")

        blacklist_token(jti, token_type="refresh", user=user)

        auth = self.context["request"].META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer "):
            try:
                ap = decode_jwt_token(auth.split()[1])
                if ap.get("type") == "access":
                    blacklist_token(ap["jti"], token_type="access", user=user)
            except Exception:
                pass
        return attrs
