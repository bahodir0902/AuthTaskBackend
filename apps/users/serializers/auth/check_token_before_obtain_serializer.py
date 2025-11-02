import logging
from typing import Any

from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.users.auth.jwt import make_jwt_token
from apps.users.auth.otp import create_otp, verify_otp
from apps.users.service import send_otp_verification

logger = logging.getLogger(__name__)

MFA_SCOPE = "mfa"


class CheckTokenBeforeObtainSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=False, allow_blank=True)
    otp_token = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[Any, Any]:
        if not attrs.get("email"):
            raise AuthenticationFailed("Email required")
        if not attrs.get("password"):
            raise AuthenticationFailed("Password required")

        user = authenticate(
            self.context.get("request"), username=attrs["email"], password=attrs["password"]
        )
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        self._check(user)

        if not getattr(user, "mfa_enabled", False):
            tokens = self._login_and_generate_tokens(user, mfa_enabled=False)
            return tokens

        token = attrs.get("otp_token")
        code = attrs.get("otp_code")

        if token and code:
            res = verify_otp(MFA_SCOPE, token, code, consume=True)
            if not res.ok:
                if res.expired_or_exceeded:
                    raise AuthenticationFailed("Code expired or too many attempts.")
                raise AuthenticationFailed("Invalid verification code.")

            uid = res.uid
            if not uid or uid is False or uid != user.id:
                logger.warning(
                    f"users.login. User with id {user.pk} entered invalid code"
                    f" with mfa enabled status."
                )
                raise AuthenticationFailed("Invalid code.", code="otp_invalid")

            tokens = self._login_and_generate_tokens(user, mfa_enabled=True)
            return tokens

        token, otp_code = create_otp("mfa", user.pk)

        send_otp_verification(user.email, user.first_name, otp_code)
        logger.info(f"users.login. OTP code sent for user id: {user.id}")
        return {"otp_required": True, "otp_token": token}

    @staticmethod
    def _check(user) -> None:
        if getattr(user, "must_set_password", False):
            logger.info(f"users.login. User {user.id} has no password set but attempted to login.")
            raise AuthenticationFailed(
                "You must set your password before logging in.",
                code="initial_password_required",
            )

        if not getattr(user, "email_verified", False):
            logger.info(
                f"users.login. User {user.id} has no email verified but attempted to login."
            )
            raise AuthenticationFailed(
                "Please verify your email before logging in.",
                code="email_not_verified",
            )

        if hasattr(user, "is_active") and not user.is_active:
            logger.warning(
                f"users.login. User {user.id} has deactivated account but attempted to login."
            )
            raise AuthenticationFailed("User account is disabled.", code="user_disabled")

    @staticmethod
    def _login_and_generate_tokens(user, mfa_enabled: bool):
        refresh, _ = make_jwt_token(user, token_type="refresh")
        access, _ = make_jwt_token(user, token_type="access")
        with transaction.atomic():
            user.last_login = timezone.now()
            user.save()
        logger.info(f"users.login. Successfully logged in {user.id} with mfa status: {mfa_enabled}")
        return {"refresh": refresh, "access": access}
