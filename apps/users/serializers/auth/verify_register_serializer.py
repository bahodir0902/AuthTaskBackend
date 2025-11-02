import logging

from decouple import config
from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.users.auth.jwt import make_jwt_token
from apps.users.auth.otp import verify_otp
from apps.users.models.user import User
from apps.users.serializers import UserSerializer

logger = logging.getLogger(__name__)

REG_SCOPE = "register"
TTL_SECONDS = config("TTL_SECONDS", 300, cast=int)


class VerifyRegisterSerializer(serializers.Serializer):
    otp_token = serializers.CharField()
    code = serializers.CharField(max_length=10)
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        if not attrs.get("email"):
            raise serializers.ValidationError("Email is required")
        if not attrs.get("otp_token"):
            raise serializers.ValidationError("otp_token is required.")
        if not attrs.get("code"):
            raise serializers.ValidationError("Verification code is required.")

        attrs["email"] = attrs["email"].lower().strip()
        return attrs

    def create(self, validated_data):
        otp_token = validated_data["otp_token"]
        code = validated_data["code"]

        res = verify_otp(REG_SCOPE, otp_token, code, consume=True)
        if not res.ok:
            if res.expired_or_exceeded:
                raise serializers.ValidationError("Code expired or too many attempts.")
            raise serializers.ValidationError("Invalid verification code.")

        meta = res.meta or {}
        email = meta.get("email")
        if not email:
            raise serializers.ValidationError("Invalid verification session.")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("User already registered in the system")

        try:
            user = User.objects.create_user(
                email=email,
                first_name=meta.get("first_name"),
                last_name=meta.get("last_name"),
            )
            user.password = meta.get("password_hash")
            user.email_verified = True
            user.must_set_password = False
            user.is_active = True
            user.save()

            user_group, _ = Group.objects.get_or_create(name="Users")
            user.groups.add(user_group)

            refresh, _ = make_jwt_token(user, token_type="refresh")
            access, _ = make_jwt_token(user, token_type="access")

            return {
                "message": "Registration completed successfully",
                "user": UserSerializer(user, context=self.context).data,
                "refresh": refresh,
                "access": access,
            }
        except Exception as e:
            print(e)
            raise serializers.ValidationError("User creation failed. Please try again later.")
