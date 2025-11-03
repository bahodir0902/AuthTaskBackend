import logging

from django.shortcuts import render
from django.views import View
from rest_framework import serializers

from apps.users.auth.jwt import make_jwt_token
from apps.users.serializers import SetInitialPasswordSerializer, ValidateInviteSerializer

logger = logging.getLogger(__name__)


class ActivateAccountView(View):
    """
    Non-REST view for handling password activation via email link.
    This is a TEMPORARY demonstration view that should be replaced by frontend.

    GET: Display password set form
    POST: Process password submission
    """

    template_form = "set_password.html"
    template_success = "password_set_success.html"

    def get(self, request):
        """Display the password set form"""
        uid = request.GET.get("uid")
        token = request.GET.get("token")

        if not uid or not token:
            return render(
                request,
                self.template_form,
                {"error": "Missing uid or token in the link", "uid": "", "token": ""},
            )

        validator = ValidateInviteSerializer(data={"uid": uid, "token": token})
        try:
            validator.is_valid(raise_exception=True)
            logger.info("[AUTH] Activation page displayed - uid=%s", uid)
            return render(request, self.template_form, {"uid": uid, "token": token})
        except serializers.ValidationError as e:
            error_msg = self._parse_error_message(e)
            logger.warning("[AUTH] Invalid activation link - uid=%s, error=%s", uid, error_msg)
            return render(
                request, self.template_form, {"error": error_msg, "uid": uid, "token": token}
            )

    def post(self, request):
        """Process the password submission"""
        uid = request.POST.get("uid")
        token = request.POST.get("token")
        new_password = request.POST.get("new_password")
        re_password = request.POST.get("re_password")

        serializer = SetInitialPasswordSerializer(
            data={
                "uid": uid,
                "token": token,
                "new_password": new_password,
                "re_password": re_password,
            },
            context={"request": request},
        )

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            refresh, _ = make_jwt_token(user, token_type="refresh")
            access, _ = make_jwt_token(user, token_type="access")

            logger.info(
                "[AUTH] Initial password set successfully via web form - user_id=%s", user.pk
            )

            return render(
                request,
                self.template_success,
                {"access_token": access, "refresh_token": refresh, "user_email": user.email},
            )

        except serializers.ValidationError as e:
            error_msg = self._format_validation_errors(e)
            logger.warning("[AUTH] Password set failed - uid=%s, error=%s", uid, error_msg)
            return render(
                request, self.template_form, {"error": error_msg, "uid": uid, "token": token}
            )

    def _parse_error_message(self, exception):
        """Parse validation error into user-friendly message"""
        if hasattr(exception, "detail"):
            detail = exception.detail
            if isinstance(detail, dict):
                if "detail" in detail:
                    if "already_activated" in str(detail["detail"]):
                        return "This account has already been activated."
                if "uid" in detail and "invalid_uid" in str(detail["uid"]):
                    return "Invalid activation link."
                if "token" in detail and "invalid_token" in str(detail["token"]):
                    return "Invalid or expired activation token."
            return str(detail)
        return "Invalid or expired activation link."

    def _format_validation_errors(self, exception):
        """Format validation errors for display"""
        if hasattr(exception, "detail"):
            detail = exception.detail
            if isinstance(detail, dict):
                errors = []
                for field, messages in detail.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            errors.append(f"{field}: {msg}")
                    else:
                        errors.append(f"{field}: {messages}")
                return " | ".join(errors) if errors else str(detail)
            return str(detail)
        return "An error occurred while setting your password."
