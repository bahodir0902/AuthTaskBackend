from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers

from apps.users.models import User


class ValidateInviteSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        uidb64 = attrs["uid"]
        token = attrs["token"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError({"uid": "invalid_uid"})

        if not user.must_set_password:
            raise serializers.ValidationError({"detail": "already_activated"})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "invalid_token"})

        attrs["user"] = user
        return attrs
