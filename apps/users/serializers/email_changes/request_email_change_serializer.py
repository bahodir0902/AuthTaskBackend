import logging

from rest_framework import serializers

from apps.users.auth.otp import create_otp
from apps.users.models import User
from apps.users.service import send_email_to_verify_email

logger = logging.getLogger(__name__)
EMAIL_SCOPE = "email_change"


class RequestEmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate(self, attrs):
        new_email = attrs.get("new_email")
        if User.objects.filter(email=new_email).exists():
            raise serializers.ValidationError(f"User with {new_email} email already exists.")

        user = self.context.get("request").user
        if not user:
            raise serializers.ValidationError("User not found")
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get("user")

        new_email = validated_data["new_email"]
        otp_token, code = create_otp(scope=EMAIL_SCOPE, uid=user.pk, meta={"new_email": new_email})
        send_email_to_verify_email(new_email, getattr(user, "first_name", "User"), code)

        return {
            "message": f"Successfully sent verification code to {new_email}",
            "otp_token": otp_token,
        }
