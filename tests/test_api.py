from api.main import app
from api.virgo_auth import SwiftAuthenticator
from fastapi import status
from fastapi.testclient import TestClient
from jose import jwt

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ping": "pong"}


def test_auth_success(mocker):
    test_username = "test_user"
    test_password = "test_pass"  # noqa: S105
    test_db_url = "http://test_url"

    mocker.patch("api.virgo_auth.SwiftAuthenticator.authenticate")

    mocker.patch.object(SwiftAuthenticator, "authenticate", return_value=200)

    payload = {
        "username": test_username,
        "password": test_password,
        "db_url": test_db_url,
    }
    response = client.post("/token", data=payload)
    assert response.status_code == status.HTTP_200_OK
    # Assert that we get the correct user from the token headers
    assert jwt.get_unverified_claims(response.json())["sub"] == test_username


def test_auth_failure_bad_auth(mocker):
    test_username = "test_user"
    test_password = "test_pass"  # noqa: S105
    test_db_url = "http://test_url"

    mocker.patch("api.virgo_auth.SwiftAuthenticator.authenticate")

    mocker.patch.object(SwiftAuthenticator, "authenticate", return_value=401)

    payload = {
        "username": test_username,
        "password": test_password,
        "db_url": test_db_url,
    }
    response = client.post("/token", data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Authentication failed"


def test_auth_failure_bad_url(mocker):
    test_username = "test_user"
    test_password = "test_pass"  # noqa: S105
    test_db_url = "http://test_url"

    mocker.patch("api.virgo_auth.SwiftAuthenticator.authenticate")

    mocker.patch.object(SwiftAuthenticator, "authenticate", return_value=404)

    payload = {
        "username": test_username,
        "password": test_password,
        "db_url": test_db_url,
    }
    response = client.post("/token", data=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Incorrect URL provided"


def test_settings_load_failure_missing_username():
    test_password = "test_pass"  # noqa: S105
    test_db_url = "http://test_url"

    payload = {
        "password": test_password,
        "db_url": test_db_url,
    }
    response = client.post("/token", data=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "username" in response.json()["detail"][0]["loc"]


def test_settings_load_failure_missing_password():
    test_user = "test_user"
    test_db_url = "http://test_url"
    payload = {
        "username": test_user,
        "db_url": test_db_url,
    }
    response = client.post("/token", data=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "password" in response.json()["detail"][0]["loc"]


def test_settings_load_failure_missing_all():
    response = client.post("/token")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "username" in response.json()["detail"][0]["loc"]
    assert "password" in response.json()["detail"][1]["loc"]
