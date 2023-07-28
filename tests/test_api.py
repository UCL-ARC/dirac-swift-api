import os

from api.auth import SwiftAuthenticator
from api.config import get_settings
from api.main import app
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ping": "pong"}


def test_auth_success(mocker):
    os.environ["VIRGO_USERNAME"] = "test_user"
    os.environ["VIRGO_PASSWORD"] = "test_pass"  # noqa: S105
    os.environ["VIRGO_DB_URL"] = "http://test_url"

    mocker.patch("api.auth.SwiftAuthenticator.authenticate")

    mocker.patch.object(SwiftAuthenticator, "authenticate", return_value=200)

    response = client.post("/auth")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["auth_result_status"] == str(status.HTTP_200_OK)


def test_auth_failure_bad_auth(mocker):
    os.environ["VIRGO_USERNAME"] = "test_user"
    os.environ["VIRGO_PASSWORD"] = "test_pass"  # noqa: S105
    os.environ["VIRGO_DB_URL"] = "http://test_url"

    mocker.patch("api.auth.SwiftAuthenticator.authenticate")

    mocker.patch.object(SwiftAuthenticator, "authenticate", return_value=401)

    response = client.post("/auth")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["auth_result_status"] == str(status.HTTP_401_UNAUTHORIZED)


def test_auth_failure_bad_url(mocker):
    os.environ["VIRGO_USERNAME"] = "test_user"
    os.environ["VIRGO_PASSWORD"] = "test_pass"  # noqa: S105
    os.environ["VIRGO_DB_URL"] = "http://test_url"

    mocker.patch("api.auth.SwiftAuthenticator.authenticate")

    mocker.patch.object(SwiftAuthenticator, "authenticate", return_value=404)

    response = client.post("/auth")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["auth_result_status"] == str(status.HTTP_404_NOT_FOUND)


def test_settings_load_failure_missing_username():
    os.environ["VIRGO_PASSWORD"] = "test_pass"  # noqa: S105
    os.environ["VIRGO_DB_URL"] = "http://test_url"
    response = client.post("/auth")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"] == "Missing fields for authentication: ['username']"
    )


def test_settings_load_failure_missing_password():
    os.environ["VIRGO_USERNAME"] = "test_user"
    os.environ["VIRGO_DB_URL"] = "http://test_url"
    response = client.post("/auth")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"] == "Missing fields for authentication: ['password']"
    )


def test_settings_load_failure_missing_url():
    os.environ["VIRGO_USERNAME"] = "test_user"
    os.environ["VIRGO_PASSWORD"] = "test_pass"  # noqa: S105
    settings = get_settings()
    response = client.post(f"/auth?{settings}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "Missing fields for authentication: ['db_url']"


def test_settings_load_failure_missing_all():
    response = client.post("/auth")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"]
        == "Missing fields for authentication: ['username', 'password', 'db_url']"
    )
