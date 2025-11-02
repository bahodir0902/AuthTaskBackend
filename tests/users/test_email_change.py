import pytest
from apps.users.auth.otp import create_otp

BASEU = "/api/accounts/users"
EMAIL_CHANGE_SCOPE = "email_change"


@pytest.mark.django_db
def test_request_email_change_requires_auth(api_client):
    r = api_client.post(f"{BASEU}/request-email-change/", {"new_email": "xx@ex.com"}, format="json")
    assert r.status_code in (401, 403)


@pytest.mark.django_db
def test_confirm_email_change_flow(api_client, user, auth_header):
    new_email = "newmail@example.com"
    otp_token, code = create_otp(EMAIL_CHANGE_SCOPE, uid=user.pk, meta={"new_email": new_email})
    r = api_client.post(f"{BASEU}/confirm-email-change/", {"otp_token": otp_token, "code": code},
                        format="json", **auth_header)
    assert r.status_code == 200
    user.refresh_from_db()
    assert user.email == new_email
