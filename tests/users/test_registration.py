import pytest
from apps.users.auth.otp import create_otp, _get_otp
from apps.users.models import User
from django.contrib.auth.hashers import make_password

BASE = "/api/accounts/auth"

REG_SCOPE = "register"


@pytest.mark.django_db
def test_register_returns_otp_token(api_client):
    r = api_client.post(
        f"{BASE}/register/",
        {"email": "new@ex.com", "first_name": "New", "last_name": "Guy", "password": "GoodP4ss!",
         "re_password": "GoodP4ss!"},
        format="json",
    )
    assert r.status_code == 200
    assert "otp_token" in r.data and r.data["email"] == "new@ex.com"


@pytest.mark.django_db
def test_verify_registration_with_precreated_otp(api_client):
    email = "reg@ex.com"
    raw_password = "123"

    meta = {
        "email": email,
        "first_name": "Reg",
        "last_name": "Ular",
        "password_hash": make_password(raw_password)
    }
    otp_token, code = create_otp(REG_SCOPE, uid=None, meta=meta)

    r = api_client.post(
        f"{BASE}/verify-registration/",
        {"otp_token": otp_token, "code": code, "email": email},
        format="json",
    )
    assert r.status_code == 201
    assert User.objects.filter(email=email).exists()
    assert "access" in r.data and "refresh" in r.data
    assert _get_otp(REG_SCOPE, otp_token) is None

    r = api_client.post(
        f"{BASE}/login/",
        {"email": "reg@ex.com", "password": "123"},
        format="json",
    )
    assert r.status_code == 200
    assert 'access' in r.data and 'refresh' in r.data

