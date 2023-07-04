import os

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

    mocker.patch("api.auth.SwiftAuthenticator.validate_credentials")
    response = client.get("/auth")

    assert response.status_code == status.HTTP_200_OK
