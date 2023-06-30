from api.auth import SwiftAuthenticator
from api.config import Settings
from fastapi import status
from pydantic import SecretStr


def test_authenticate_success(data_path, mocker):
    mocker.patch("api.auth.SwiftAuthenticator.load_cookies")
    mocked_response = mocker.patch("requests.Response")
    mocked_response.return_value.status_code.return_value = status.HTTP_200_OK

    test_user = "test1"
    test_pass = SecretStr("pass")
    test_url = "test_url"
    settings = Settings(username=test_user, password=test_pass, db_url=test_url)

    cookies_file = data_path / "cookies.txt"
    auth = SwiftAuthenticator(settings, cookies_file)

    result = auth.authenticate()
    assert result is True


def test_save_cookies():
    pass


def test_load_cookies():
    pass
