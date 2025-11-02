import logging

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from apps.users.auth.otp import verify_otp
from apps.users.models import User

logger = logging.getLogger(__name__)
PWD_SCOPE = "pwd_reset"


class VerifyPasswordResetSerializer(serializers.Serializer):
    otp_token = serializers.CharField()
    code = serializers.CharField(max_length=10)

    def validate(self, attrs):
        if not attrs.get("otp_token") or not attrs.get("code"):
            raise serializers.ValidationError("otp_token and code are required.")
        return attrs

    def create(self, validated_data):
        otp_token = validated_data["otp_token"]
        code = validated_data["code"]

        res = verify_otp(PWD_SCOPE, otp_token, code, consume=True)
        if not res.ok:
            if res.expired_or_exceeded:
                logger.warning("users.verify_password_reset. code expired or too many attempts.")
                raise serializers.ValidationError("Code expired or too many attempts.")
            logger.warning("users.verify_password_reset. invalid code.")
            raise serializers.ValidationError("Invalid code.")

        uid = res.uid
        email = (res.meta or {}).get("email")
        user = User.objects.filter(pk=uid, email=email).first()
        if not user:
            logger.warning("users.verify_password_reset. no user found.")
            raise serializers.ValidationError("User not found.")

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        return {
            "message": "Code verified successfully. You can now reset your password.",
            "uid": uidb64,
            "token": token,
        }
