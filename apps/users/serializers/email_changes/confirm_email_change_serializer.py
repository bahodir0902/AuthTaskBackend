import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.users.auth.otp import verify_otp
from apps.users.models import User

logger = logging.getLogger(__name__)
EMAIL_SCOPE = "email_change"


class ConfirmEmailChangeSerializer(serializers.Serializer):
    otp_token = serializers.CharField()
    code = serializers.CharField(max_length=10)

    def validate(self, attrs):
        token = attrs.get("otp_token")
        code = attrs.get("code")
        if not token or not code:
            raise ValidationError("otp_token and code are required.")

        res = verify_otp(EMAIL_SCOPE, token, code, consume=True)
        if not res.ok:
            if res.expired_or_exceeded:
                raise ValidationError("Your code has expired or too many attempts.")
            raise ValidationError("Incorrect code. Please enter the correct code.")

        uid = res.uid
        new_email = (res.meta or {}).get("new_email")
        user = User.objects.filter(pk=uid).first()
        if not user or not new_email:
            raise ValidationError("Invalid or expired session.")

        attrs["user"] = user
        attrs["new_email"] = new_email
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        new_email = validated_data["new_email"]
        user.email = new_email
        user.save()
        return {"message": "Successfully changed to new email"}
