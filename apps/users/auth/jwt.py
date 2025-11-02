import uuid
from datetime import datetime, timezone

import jwt
from django.conf import settings

from apps.users.models import BlacklistedToken, IssuedRefreshToken


def _now():
    return datetime.now(timezone.utc)


def make_jwt_token(user, token_type="access"):
    now = _now()
    jti = str(uuid.uuid4())
    if token_type == "access":
        exp = now + settings.JWT_ACCESS_LIFETIME
    elif token_type == "refresh":
        exp = now + settings.JWT_REFRESH_LIFETIME
    else:
        raise ValueError("token type must be 'access' or 'refresh'")

    payload = {
        "jti": jti,
        "user_id": user.pk,
        "type": token_type,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "iss": getattr(settings, "JWT_ISSUER", None),
        "aud": getattr(settings, "JWT_AUDIENCE", None),
    }

    payload = {k: v for k, v in payload.items() if v is not None}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    if token_type == "refresh":
        IssuedRefreshToken.objects.create(
            jti=payload["jti"],
            user=user,
            expires_at=exp,
        )

    return token, payload


def decode_jwt_token(token, verify_exp=True):
    options = {"verify_exp": verify_exp}
    try:
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options=options,
            issuer=getattr(settings, "JWT_ISSUER", None),
            audience=getattr(settings, "JWT_AUDIENCE", None),
        )
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidTokenError:
        raise
    return decoded


def is_blacklisted(jti):
    return BlacklistedToken.objects.filter(jti=jti).exists()


from apps.users.models.auth.blacklist_token import TokenType  # noqa


def blacklist_token(jti, token_type="refresh", user=None):
    token_type = (token_type or "refresh").lower()
    if token_type not in (TokenType.ACCESS, TokenType.REFRESH):
        raise ValueError("token type must be 'access' or 'refresh'")
    BlacklistedToken.objects.get_or_create(
        jti=jti, defaults={"token_type": token_type, "user": user}
    )
    if token_type == TokenType.REFRESH:
        IssuedRefreshToken.objects.filter(jti=jti).update(revoked=True)
