import logging
from typing import Any

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.users.models import BlacklistedToken, IssuedRefreshToken, User
from apps.users.models.auth.blacklist_token import TokenType

logger = logging.getLogger(__name__)
PWD_SCOPE = "pwd_reset"


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    re_new_password = serializers.CharField(write_only=True, required=True)
    uid = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("re_new_password"):
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data: dict[str, Any]):
        uidb64 = validated_data["uid"]
        token = validated_data["token"]
        new_password = validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            logger.warning("users.reset_password... user provided invalid uid.")
            raise serializers.ValidationError("Invalid user.")

        if not default_token_generator.check_token(user, token):
            logger.warning("users.reset_password... user provided invalid token.")
            raise serializers.ValidationError("Invalid or expired token.")

        user.set_password(new_password)
        user.must_set_password = False
        user.email_verified = True
        user.save()

        for t in IssuedRefreshToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(
                jti=t.jti, defaults={"token_type": TokenType.REFRESH, "user": user}
            )

        return {"message": "Password has been reset successfully."}
