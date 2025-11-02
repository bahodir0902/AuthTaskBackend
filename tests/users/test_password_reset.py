import pytest
from apps.users.auth.otp import create_otp

BASE = "/api/accounts/auth"
PWD_RESET_SCOPE = "pwd_reset"


@pytest.mark.django_db
def test_forgot_password_sends_code(api_client, user):
    r = api_client.post(f"{BASE}/forgot-password/", {"email": user.email}, format="json")
    assert r.status_code == 202
    assert r.data["email"] == user.email
    assert "otp_token" in r.data


@pytest.mark.django_db
def test_verify_and_reset_password(api_client, user):
    otp_token, code = create_otp(PWD_RESET_SCOPE, uid=user.pk, meta={"email": user.email})
    v = api_client.post(
        f"{BASE}/verify-password-reset/", {
            "otp_token": otp_token,
            "code": code
        }, format="json"
    )
    assert v.status_code == 200
    uid = v.data["uid"]
    token = v.data["token"]

    r = api_client.post(
        f"{BASE}/reset-password/", {
            "uid": uid,
            "token": token,
            "new_password": "NewP4ss!",
            "re_new_password": "NewP4ss!"
        }, format="json",
    )

    assert r.status_code == 200
    ok = api_client.post(
        f"{BASE}/login/", {
            "email": user.email,
            "password": "NewP4ss!"
        }, format="json"
    )
    assert ok.status_code == 200
