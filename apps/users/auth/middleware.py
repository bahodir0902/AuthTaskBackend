from django.utils.deprecation import MiddlewareMixin

from apps.users.models import User

from .jwt import decode_jwt_token, is_blacklisted


class JWTMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth:
            return None

        parts = auth.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        token = parts[1]

        try:
            payload = decode_jwt_token(token=token, verify_exp=True)
        except Exception:
            return None

        if payload.get("type") != "access":
            return None

        jti = payload.get("jti")
        if is_blacklisted(jti):
            return None

        user_id = payload.get("user_id")
        user = User.objects.filter(pk=user_id).first()

        if not user:
            return None

        request.user = user
        request.jwt_payload = payload
        request._auth = token
        return None
