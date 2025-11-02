import logging

from rest_framework import serializers

from apps.users.auth.otp import create_otp
from apps.users.models import User
from apps.users.service import send_password_verification

logger = logging.getLogger(__name__)
PWD_SCOPE = "pwd_reset"


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email doesn't exist.")
        return value

    def create(self, validated_data):
        email = validated_data["email"].lower().strip()
        user = User.objects.get(email=email)
        otp_token, code = create_otp(scope=PWD_SCOPE, uid=user.pk, meta={"email": email})
        send_password_verification(email, user.first_name, code)
        return {
            "message": "Password reset code has been sent to your email.",
            "email": email,
            "otp_token": otp_token,
        }
