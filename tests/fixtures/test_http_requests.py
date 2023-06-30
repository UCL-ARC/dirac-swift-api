import pytest
from fastapi import status
from requests import Response


@pytest.fixture()
def mock_successful_response(mocker):
    successful_response_mock = mocker.MagicMock(
        name="successful_response_mock",
        spec=Response,
    )
    successful_response_mock.status_code = status.HTTP_200_OK

    return successful_response_mock
