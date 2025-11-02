import os

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.users.auth.jwt import make_jwt_token


@pytest.fixture(autouse=True, scope="session")
def _test_env_vars():
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("EMAIL_BACKEND", "django.core.mail.backends.locmem.EmailBackend")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def User():
    return get_user_model()


@pytest.fixture
def user(User):
    u = User.objects.create_user(
        email="user@example.com",
        password="Passw0rd!",
        first_name="U",
        last_name="S",
        is_active=True,
    )
    u.email_verified = True
    u.must_set_password = False
    u.save(update_fields=["email_verified", "must_set_password"])
    return u


@pytest.fixture
def access_token(user):
    token, _ = make_jwt_token(user, "access")
    return token


@pytest.fixture
def auth_header(access_token):
    return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}


@pytest.fixture(autouse=True)
def _flush_emails():
    mail.outbox.clear()
    yield
    mail.outbox.clear()


@pytest.fixture(autouse=True)
def _flush_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def settings_test():
    from core import settings_test

    return settings_test
