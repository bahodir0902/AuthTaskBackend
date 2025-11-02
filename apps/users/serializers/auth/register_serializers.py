import logging
from typing import Any

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.users.auth.otp import create_otp
from apps.users.models.user import User
from apps.users.service import send_email_verification

logger = logging.getLogger(__name__)

REG_SCOPE = "register"


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, max_length=255)
    re_password = serializers.CharField(write_only=True, max_length=255)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        password = attrs.get("password")
        re_password = attrs.get("re_password")
        if not password or not re_password:
            raise serializers.ValidationError("Please provide password")

        if str(password) != str(re_password):
            raise serializers.ValidationError("Passwords don't match")

        email = attrs.get("email")
        if not email:
            raise serializers.ValidationError("No email provided.")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User already registered in the system")

        return attrs

    def create(self, validated_data: dict[str, Any]):
        vd = dict(validated_data)
        email = vd["email"].lower().strip()
        raw_password = vd.pop("password")
        vd.pop("re_password", None)

        pending_meta = {
            **vd,
            "email": email,
            "password_hash": make_password(raw_password),
        }

        otp_token, code = create_otp(scope=REG_SCOPE, uid=None, meta=pending_meta)
        send_email_verification(email, vd.get("first_name"), code)

        return {
            "message": "Verification code sent to your email. Please verify"
            " to complete registration.",
            "email": email,
            "otp_token": otp_token,
        }
