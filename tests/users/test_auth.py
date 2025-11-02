import pytest
from apps.users.auth.otp import create_otp
from apps.users.auth.jwt import decode_jwt_token
from apps.users.models import IssuedRefreshToken, BlacklistedToken

BASE = "/api/accounts/auth"


@pytest.mark.django_db
def test_login_success_no_mfa(api_client, user):
    res = api_client.post(
        f"{BASE}/login/", {
            "email": user.email,
            "password": "Passw0rd!"
        }, format="json"
    )
    assert res.status_code == 200
    assert "access" in res.data and "refresh" in res.data

    payload = decode_jwt_token(res.data["refresh"])
    assert IssuedRefreshToken.objects.filter(jti=payload["jti"], user=user, revoked=False).exists()


@pytest.mark.django_db
def test_login_mfa_challenge_then_verify(api_client, user):
    user.mfa_enabled = True
    user.save(update_fields=["mfa_enabled"])

    r1 = api_client.post(f"{BASE}/login/", {"email": user.email, "password": "Passw0rd!"},
                         format="json")
    assert r1.status_code == 200
    assert r1.data["otp_required"] is True
    assert "otp_token" in r1.data

    otp_token, code = create_otp("mfa", user.pk)
    r2 = api_client.post(
        f"{BASE}/login/",
        {"email": user.email, "password": "Passw0rd!", "otp_token": otp_token, "otp_code": code},
        format="json",
    )
    assert r2.status_code == 200
    assert "access" in r2.data and "refresh" in r2.data


@pytest.mark.django_db
def test_refresh_rotates_and_revokes_old(api_client, user):
    r = api_client.post(f"{BASE}/login/", {"email": user.email, "password": "Passw0rd!"},
                        format="json")
    old_refresh = r.data["refresh"]
    old_payload = decode_jwt_token(old_refresh)
    assert IssuedRefreshToken.objects.filter(jti=old_payload["jti"], revoked=False).exists()

    r2 = api_client.post(f"{BASE}/refresh/", {"refresh": old_refresh}, format="json")
    assert r2.status_code == 200
    new_refresh = r2.data["refresh"]
    new_payload = decode_jwt_token(new_refresh)

    assert BlacklistedToken.objects.filter(jti=old_payload["jti"]).exists()
    assert IssuedRefreshToken.objects.filter(jti=old_payload["jti"], revoked=True).exists()

    assert IssuedRefreshToken.objects.filter(jti=new_payload["jti"], revoked=False).exists()


@pytest.mark.django_db
def test_logout_revokes_refresh_and_blacklists_access(api_client, user):
    r = api_client.post(f"{BASE}/login/", {"email": user.email, "password": "Passw0rd!"},
                        format="json")
    refresh = r.data["refresh"]
    access = r.data["access"]

    res = api_client.post(
        f"{BASE}/logout/",
        {"refresh": refresh},
        format="json",
        HTTP_AUTHORIZATION=f"Bearer {access}",
    )
    assert res.status_code == 200

    p = decode_jwt_token(refresh)
    assert BlacklistedToken.objects.filter(jti=p["jti"]).exists()
    assert IssuedRefreshToken.objects.filter(jti=p["jti"], revoked=True).exists()


@pytest.mark.django_db
def test_logout_all_devices_revokes_all(api_client, user):
    r1 = api_client.post(f"{BASE}/login/", {"email": user.email, "password": "Passw0rd!"},
                         format="json")
    api_client.post(f"{BASE}/login/", {"email": user.email, "password": "Passw0rd!"},
                         format="json")
    access = r1.data["access"]

    res = api_client.post(f"{BASE}/logout-of-all-devices/", {},
                          HTTP_AUTHORIZATION=f"Bearer {access}")
    assert res.status_code == 200
    assert IssuedRefreshToken.objects.filter(user=user, revoked=True).count() >= 2
