import json
from pathlib import Path

from api.auth import SwiftAuthenticator
from fastapi import status
from requests import Session
from requests.exceptions import RequestException


def test_authenticate_success(data_path, mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get")
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=200)

    cookies_file = data_path / "cookies.txt"
    auth = SwiftAuthenticator(mock_settings, cookies_file)

    result = auth.authenticate()

    cookie_save.assert_called_once()
    assert result == status.HTTP_200_OK


def test_authenticate_failure_auth(data_path, mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get")
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=401)

    cookies_file = data_path / "cookies.txt"
    auth = SwiftAuthenticator(mock_settings, cookies_file)

    result = auth.authenticate()

    cookie_save.assert_not_called()
    assert result == status.HTTP_401_UNAUTHORIZED


def test_authenticate_failure_bad_url(data_path, mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get", side_effect=RequestException)
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=401)

    cookies_file = data_path / "cookies.txt"
    auth = SwiftAuthenticator(mock_settings, cookies_file)

    result = auth.authenticate()

    cookie_save.assert_not_called()
    assert result == status.HTTP_404_NOT_FOUND


def test_save_cookies_success(temp_out_dir, mock_settings):
    test_session = Session()
    test_session.cookies.set("SESSIONID", "TESTSESSION", domain="test")

    cookies_file = temp_out_dir / "cookies.txt"
    auth = SwiftAuthenticator(mock_settings, cookies_file)
    auth.save_cookies(test_session)
    with cookies_file.open("r") as cookies:
        contents = json.load(cookies)
        assert contents["SESSIONID"] == "TESTSESSION"


def test_save_cookies_failure(temp_out_dir, mock_settings):
    test_session = Session()

    cookies_file = Path(temp_out_dir / "cookies.txt")
    auth = SwiftAuthenticator(mock_settings, cookies_file)
    auth.save_cookies(test_session)
    with cookies_file.open("r") as cookies:
        contents = json.load(cookies)
        assert "SESSIONID" not in contents


def test_load_cookies(mock_settings, data_path):
    test_session = Session()

    cookies_file = data_path / "cookies.txt"
    auth = SwiftAuthenticator(mock_settings, cookies_file)
    auth.load_cookies(test_session)

    cookies_dict = test_session.cookies.get_dict()
    assert len(cookies_dict.keys()) == 1
    assert "SESSIONID" in cookies_dict
    assert cookies_dict["SESSIONID"] == "TESTSESSION"
