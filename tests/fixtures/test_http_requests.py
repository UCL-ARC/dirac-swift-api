import pytest
from api.config import Settings
from fastapi import status
from pydantic import SecretStr


@pytest.fixture()
def mock_successful_response(mocker):
    successful_response_mock = mocker.MagicMock(
        name="successful_response_mock",
    )
    successful_response_mock.return_value.status_code = status.HTTP_200_OK

    return successful_response_mock


@pytest.fixture()
def mock_settings():
    test_user = "test1"
    test_pass = SecretStr("pass")
    test_url = "test_url"
    return Settings(username=test_user, password=test_pass, db_url=test_url)
