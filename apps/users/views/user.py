import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from apps.users.auth.jwt import make_jwt_token
from apps.users.models import BlacklistedToken, IssuedRefreshToken, User, UserProfile
from apps.users.models.auth.blacklist_token import TokenType
from apps.users.serializers import (
    CheckTokenBeforeObtainSerializer,
    ConfirmEmailChangeSerializer,
    CustomTokenRefreshSerializer,
    ForgotPasswordSerializer,
    LogoutSerializer,
    RegisterSerializer,
    RequestEmailChangeSerializer,
    ResetPasswordSerializer,
    SetInitialPasswordSerializer,
    UserProfileReadSerializer,
    UserProfileWriteSerializer,
    UserSerializer,
    ValidateInviteSerializer,
    VerifyPasswordResetSerializer,
    VerifyRegisterSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=["Auth"])
class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    throttle_classes = [ScopedRateThrottle]

    def get_serializer_class(self):
        serializer_map = {
            "login": CheckTokenBeforeObtainSerializer,
            "refresh": CustomTokenRefreshSerializer,
            "register": RegisterSerializer,
            "verify_registration": VerifyRegisterSerializer,
            "forgot_password": ForgotPasswordSerializer,
            "verify_password_reset": VerifyPasswordResetSerializer,
            "reset_password": ResetPasswordSerializer,
            "logout": LogoutSerializer,
            "set_initial_password": SetInitialPasswordSerializer,
            "validate_invitation": ValidateInviteSerializer,
        }
        return serializer_map.get(self.action, RegisterSerializer)

    def get_permissions(self):
        if self.action in ["logout", "logout_of_all_devices"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_throttles(self):
        scope_map = {
            "login": "auth_login",
            "verify_registration": "auth_verify_registration",
            "verify_password_reset": "auth_verify_password_reset",
        }
        self.throttle_scope = scope_map.get(self.action)
        return super().get_throttles()

    @action(methods=["post"], detail=False, url_path="login")
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = serializer.save()
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="verify-registration")
    @transaction.atomic
    def verify_registration(self, request):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info("[AUTH] Registration verified successfully")
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="forgot-password")
    @transaction.atomic
    def forgot_password(self, request):
        logger.info("[AUTH] Password reset requested")
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info("[AUTH] Password reset email sent")
        return Response(result, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="verify-password-reset")
    @transaction.atomic
    def verify_password_reset(self, request):
        logger.info("[AUTH] Password reset code verification started")
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info("[AUTH] Password reset code verified, tokens issued")
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="reset-password")
    @transaction.atomic
    def reset_password(self, request):
        logger.info("[AUTH] Password reset initiated")
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info("[AUTH] Password reset completed successfully")
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def logout(self, request):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        logger.info("[AUTH] User logged out - user_id=%s", request.user.pk)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="logout-of-all-devices")
    @transaction.atomic
    def logout_of_all_devices(self, request):
        user = request.user
        i = 0
        for token in IssuedRefreshToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(jti=token.jti, token_type="refresh", user=user)
            token.revoked = True
            token.save()
            i += 1
        logger.info("[AUTH] User logged out of all devices - user_id=%s, devices=%s", user.pk, i)
        return Response(
            {"message": f"Successfully logged out of {i} devices."},
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False, url_path="set-initial-password")
    def set_initial_password(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh, _ = make_jwt_token(user, token_type="refresh")
        access, _ = make_jwt_token(user, token_type="access")
        logger.info("[AUTH] Initial password set successfully - user_id=%s", user.pk)
        return Response(
            {
                "message": "Password set successfully. You can now log in.",
                "refresh": refresh,
                "access": access,
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False, url_path="validate-invitation")
    def validate_invitation(self, request):
        s = self.get_serializer(data=request.data)
        logger.info("[AUTH] Invitation validation requested")
        s.is_valid(raise_exception=True)
        return Response({"valid": True}, status=status.HTTP_200_OK)


@extend_schema(tags=["User"])
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "update_profile":
            return UserProfileWriteSerializer
        elif self.action == "profile":
            return UserProfileReadSerializer
        elif self.action == "request_email_change":
            return RequestEmailChangeSerializer
        elif self.action == "confirm_email_change":
            return ConfirmEmailChangeSerializer
        return UserSerializer

    @action(detail=False, methods=["get"])
    def profile(self, request):
        user = request.user
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            logger.warning("[USER] Profile not found - user_id=%s", user.pk)
            return Response({"message": "User has no profile."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @extend_schema(responses=UserProfileReadSerializer)
    @action(
        detail=False,
        methods=["put", "patch"],
        parser_classes=(MultiPartParser, FormParser, JSONParser),
        url_path="update-profile",
    )
    @transaction.atomic
    def update_profile(self, request):
        profile = get_object_or_404(UserProfile.objects.select_related("user"), user=request.user)
        serializer = self.get_serializer(
            instance=profile,
            data=request.data,
            partial=(request.method == "PATCH"),
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = UserProfileReadSerializer(instance, context=self.get_serializer_context())
        logger.info("[USER] Profile updated - user_id=%s", request.user.pk)
        return Response(response.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="request-email-change")
    @transaction.atomic
    def request_email_change(self, request):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info("[USER] Email change requested - user_id=%s", request.user.pk)
        return Response(result, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], url_path="confirm-email-change")
    @transaction.atomic
    def confirm_email_change(self, request):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info("[USER] Email change confirmed - user_id=%s", request.user.pk)
        return Response(result, status=status.HTTP_200_OK)

    @action(methods=["delete"], detail=False, url_path="delete-account")
    @transaction.atomic
    def delete_account(self, request):
        user = request.user
        for t in IssuedRefreshToken.objects.filter(user=user, revoked=False):
            BlacklistedToken.objects.get_or_create(
                jti=t.jti, defaults={"token_type": TokenType.REFRESH, "user": user}
            )
            t.revoked = True
            t.save(update_fields=["revoked"])
        uid = user.pk
        user.delete()
        logger.info("[USER] Account deleted - user_id=%s", uid)
        return Response(status=status.HTTP_204_NO_CONTENT)
