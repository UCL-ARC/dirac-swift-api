import pytest
from api.config import Settings
from api.main import app
from fastapi import status
from fastapi.testclient import TestClient


@pytest.fixture()
def mock_successful_response(mocker):
    successful_response_mock = mocker.MagicMock(
        name="successful_response_mock",
    )
    successful_response_mock.return_value.status_code = status.HTTP_200_OK

    return successful_response_mock


@pytest.fixture()
def mock_settings():
    return Settings(
        db_url="http://a/test/url",
        jwt_secret_key="a_test_key",  # noqa: S106
    )


@pytest.fixture()
def mock_auth_token():
    return "auth_token"


@pytest.fixture()
def mock_auth_client_success_jwt_decode(mock_auth_token, mocker):
    client = TestClient(app)
    client.headers = {"Authorization": f"Bearer {mock_auth_token}"}
    mocker.patch("api.routers.auth.decode_jwt", return_value="test_user")
    return client
