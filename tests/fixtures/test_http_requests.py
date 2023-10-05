import pytest
from api.config import Settings
from fastapi import status


@pytest.fixture()
def mock_successful_response(mocker):
    successful_response_mock = mocker.MagicMock(
        name="successful_response_mock",
    )
    successful_response_mock.return_value.status_code = status.HTTP_200_OK

    return successful_response_mock


@pytest.fixture()
def mock_settings():
    test_url = "test_url"
    return Settings(
        db_url=test_url,
    )
