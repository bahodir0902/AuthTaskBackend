from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.users.models import User


class SetInitialPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    re_password = serializers.CharField(required=True, write_only=True)

    # def validate_new_password(self, value):
    #     validate_password(value)
    #     return value

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        re_password = attrs.get("re_password")

        if str(new_password) != str(re_password):
            raise serializers.ValidationError({"re_password": "Passwords do not match."})

        uidb64 = attrs.get("uid")
        token = attrs.get("token")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid link or token")

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError("Invalid link or token")

        if not getattr(user, "must_set_password", False):
            raise serializers.ValidationError("Password already set")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        new_password = validated_data["new_password"]

        user.set_password(new_password)
        user.is_active = True

        user.email_verified = True
        user.must_set_password = False
        user.save(update_fields=["password", "is_active", "email_verified", "must_set_password"])
        return user
