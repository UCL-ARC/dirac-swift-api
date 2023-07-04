import json
from pathlib import Path

from api.auth import SwiftAuthenticator
from fastapi import status
from requests import Session
from requests.exceptions import RequestException


def test_authenticate_success(mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get")
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=200)

    auth = SwiftAuthenticator(mock_settings)

    result = auth.authenticate()

    cookie_save.assert_called_once()
    assert result == status.HTTP_200_OK


def test_authenticate_failure_auth(mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get")
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=401)

    auth = SwiftAuthenticator(mock_settings)

    result = auth.authenticate()

    cookie_save.assert_not_called()
    assert result == status.HTTP_401_UNAUTHORIZED


def test_authenticate_failure_bad_url(mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get", side_effect=RequestException)
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=401)

    auth = SwiftAuthenticator(mock_settings)

    result = auth.authenticate()

    cookie_save.assert_not_called()
    assert result == status.HTTP_404_NOT_FOUND


def test_save_cookies_success(temp_out_dir, mock_settings):
    test_session = Session()
    test_session.cookies.set("SESSIONID", "TESTSESSION", domain="test")
    test_cookies = Path(temp_out_dir / "temp_cookies.txt")
    auth = SwiftAuthenticator(mock_settings, cookies_file=test_cookies)
    auth.save_cookies(test_session)
    with test_cookies.open("r") as cookies:
        contents = json.load(cookies)
        assert contents["SESSIONID"] == "TESTSESSION"


def test_save_cookies_failure(temp_out_dir, mock_settings):
    test_session = Session()
    test_cookies = Path(temp_out_dir / "cookies.txt")
    auth = SwiftAuthenticator(mock_settings, cookies_file=test_cookies)
    auth.save_cookies(test_session)
    with test_cookies.open("r") as cookies:
        contents = json.load(cookies)
        assert "SESSIONID" not in contents


def test_load_cookies(mock_settings, data_path):
    test_session = Session()
    test_cookies = Path(data_path / "cookies.txt")
    auth = SwiftAuthenticator(mock_settings, cookies_file=test_cookies)
    auth.load_cookies(test_session)

    cookies_dict = test_session.cookies.get_dict()
    assert len(cookies_dict.keys()) == 1
    assert "SESSIONID" in cookies_dict
    assert cookies_dict["SESSIONID"] == "TESTSESSION"
