import pytest

BASEU = "/api/accounts/users"


@pytest.mark.django_db
def test_profile_read_and_update(api_client, user, auth_header):
    r = api_client.get(f"{BASEU}/profile/", **auth_header)
    assert r.status_code == 200
    assert r.data["user"]["email"] == user.email

    r2 = api_client.patch(
        f"{BASEU}/update-profile/", {
            "first_name": "New",
            "last_name": "Name",
            "mfa_enabled": True
        }, format="json",
        **auth_header,
    )
    assert r2.status_code == 200
    assert r2.data["user"]["first_name"] == "New"
    assert r2.data["user"]["last_name"] == "Name"


@pytest.mark.django_db
def test_delete_account_soft_delete(api_client, user, auth_header):
    r = api_client.delete(f"{BASEU}/delete-account/", **auth_header)
    assert r.status_code == 204
    user.refresh_from_db()
    assert user.is_active is False
