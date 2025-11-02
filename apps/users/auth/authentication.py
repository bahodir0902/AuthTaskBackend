import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import User

from .jwt import decode_jwt_token, is_blacklisted


class JWTAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            return None

        token = parts[1]
        try:
            payload = decode_jwt_token(token, verify_exp=True)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Access token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        if payload.get("type") != "access":
            raise AuthenticationFailed("Not an access token")

        jti = payload.get("jti")
        if is_blacklisted(jti):
            raise AuthenticationFailed("Token revoked")

        user_id = payload.get("user_id")
        user = User.objects.filter(pk=user_id).first()

        if not user:
            raise AuthenticationFailed("No such user")

        if not user.is_active:
            raise AuthenticationFailed("User disabled")

        return user, payload
