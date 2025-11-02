import secrets
import uuid
from dataclasses import dataclass
from typing import Optional

from decouple import config
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache

OTP_LEN = config("OTP_LEN", cast=int, default=6)
TTL_SECONDS = config("TTL_SECONDS", cast=int, default=300)
MAX_ATTEMPTS = config("MAX_ATTEMPTS", cast=int, default=5)
DEFAULT_SCOPE = "mfa"


@dataclass
class VerifyResult:
    ok: bool
    expired_or_exceeded: bool
    uid: Optional[int] = None
    meta: dict = None


def _cache_key(scope: str, token: str) -> str:
    return f"otp:{scope}:{token}"


def _get_redis_ttl(key):
    try:
        ttl = cache.ttl(key)
        return ttl if ttl and ttl > 0 else None
    except Exception:
        pass
    try:
        from django_redis import get_redis_connection

        conn = get_redis_connection("default")
        ttl = conn.ttl(key)
        return ttl if ttl and ttl > 0 else None
    except Exception:
        return None


def _save_otp(scope, token, data, ttl=TTL_SECONDS) -> None:
    ttl_to_use = TTL_SECONDS if ttl is None else ttl
    cache.set(_cache_key(scope, token), data, ttl_to_use)


def _get_otp(scope, token) -> Optional[dict]:
    return cache.get(_cache_key(scope, token))


def _delete_otp(scope, token) -> None:
    cache.delete(_cache_key(scope, token))


def create_otp(scope=DEFAULT_SCOPE, uid=None, meta=None) -> tuple[str, str]:
    code = f"{secrets.randbelow(10 ** OTP_LEN):0{OTP_LEN}d}"
    token = str(uuid.uuid4())
    data = {
        "uid": uid,
        "meta": meta or {},
        "code": make_password(code),
        "attempts": 0,
    }
    _save_otp(scope, token, data)
    return token, code


def verify_otp(scope, token, code, *, consume=True) -> VerifyResult:
    data = _get_otp(scope, token)
    if not data:
        return VerifyResult(ok=False, expired_or_exceeded=True)

    if data["attempts"] >= MAX_ATTEMPTS:
        _delete_otp(scope, token)
        return VerifyResult(ok=False, expired_or_exceeded=True)

    if not check_password(code, data["code"]):
        data["attempts"] += 1
        cache_key = _cache_key(scope, token)
        remaining_ttl = _get_redis_ttl(cache_key)
        _save_otp(scope, token, data, remaining_ttl)
        return VerifyResult(ok=False, expired_or_exceeded=False, uid=data["uid"], meta=data["meta"])

    if consume:
        _delete_otp(scope, token)
    return VerifyResult(ok=True, expired_or_exceeded=False, uid=data["uid"], meta=data["meta"])
