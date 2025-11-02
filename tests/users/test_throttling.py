import pytest

BASE = "/api/accounts/auth"


@pytest.mark.django_db
def test_login_throttled(api_client, user, settings_test):
    ratelimit = settings_test.RATE_LIMIT
    for i in range(ratelimit):
        r1 = api_client.post(f"{BASE}/login/", {
            "email": user.email,
            "password": "Passw0rd!"
        }, format="json"
                             )
        assert r1.status_code == 200

    r2 = api_client.post(f"{BASE}/login/", {
        "email": user.email,
        "password": "Passw0rd!"
    }, format="json"
                         )
    assert r2.status_code == 429


@pytest.mark.django_db
def test_verify_registration_throttled(api_client, settings_test):
    ratelimit = settings_test.RATE_LIMIT
    for i in range(ratelimit):
        r = api_client.post(
            f"{BASE}/verify-registration/", {
                "otp_token": "x",
                "code": "y",
                "email": "a@b.com"
            }, format="json"
        )
        assert r.status_code in (400, 404, 422)
    r2 = api_client.post(
        f"{BASE}/verify-registration/", {
            "otp_token": "x",
            "code": "y",
            "email": "a@b.com"
        }, format="json"
    )
    assert r2.status_code == 429


@pytest.mark.django_db
def test_verify_password_reset_throttled(api_client, settings_test):
    ratelimit = settings_test.RATE_LIMIT
    for i in range(ratelimit):
        r = api_client.post(
            f"{BASE}/verify-password-reset/", {
                "otp_token": "x",
                "code": "y"
            }, format="json"
        )
        assert r.status_code in (400, 403, 404, 422)
    r3 = api_client.post(f"{BASE}/verify-password-reset/", {
        "otp_token": "x",
        "code": "y"
    }, format="json"
                         )
    assert r3.status_code == 429
