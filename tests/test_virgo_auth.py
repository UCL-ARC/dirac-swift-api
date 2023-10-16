import json
from pathlib import Path

from api.virgo_auth import SwiftAuthenticator
from fastapi import status
from requests import Session
from requests.exceptions import RequestException
import jwt
import datetime



def test_authenticate_success(mock_settings, mocker):
    cookie_save = mocker.patch.object(
        SwiftAuthenticator,
        "save_cookies",
        return_value=Session,
    )
    mock_get = mocker.patch.object(Session, "get")
    type(mock_get.return_value).status_code = mocker.PropertyMock(return_value=200)

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105
    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )

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

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105

    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )

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

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105

    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )

    result = auth.authenticate()

    cookie_save.assert_not_called()
    assert result == status.HTTP_404_NOT_FOUND


def test_save_cookies_success(temp_out_dir, mock_settings):
    test_session = Session()
    test_session.cookies.set("SESSIONID", "TESTSESSION", domain="test")
    test_cookies = Path(temp_out_dir / "temp_cookies.txt")

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105

    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
        cookies_file=test_cookies,
    )

    auth.save_cookies(test_session)
    with test_cookies.open("r") as cookies:
        contents = json.load(cookies)
        assert contents["SESSIONID"] == "TESTSESSION"


def test_save_cookies_failure(temp_out_dir, mock_settings):
    test_session = Session()
    test_cookies = Path(temp_out_dir / "cookies.txt")

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105

    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
        cookies_file=test_cookies,
    )
    auth.save_cookies(test_session)
    with test_cookies.open("r") as cookies:
        contents = json.load(cookies)
        assert "SESSIONID" not in contents


def test_load_cookies(mock_settings, data_path):
    test_session = Session()
    test_cookies = Path(data_path / "cookies.txt")

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105

    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
        cookies_file=test_cookies,
    )

    auth.load_cookies(test_session)

    cookies_dict = test_session.cookies.get_dict()
    assert len(cookies_dict.keys()) == 1
    assert "SESSIONID" in cookies_dict
    assert cookies_dict["SESSIONID"] == "TESTSESSION"


def test_generate_token(mock_settings, mocker):
    mocker.patch.dict('os.environ', {'JWT_SECRET_KEY': 'mysecret'})

    mock_datetime = mocker.patch('datetime.datetime')
    mock_datetime.utcnow.return_value = datetime.datetime(2022, 1, 1)

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105
    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )

    generated_token = auth.generate_token()


    decoded = jwt.decode(generated_token, 'mysecret', algorithms=['HS256'])
    expected_exp = datetime.datetime(2022, 1, 1, 1, 0)  # 1 hour added to utcnow
    expected_exp_unix = expected_exp.timestamp()

    assert decoded['exp'] == expected_exp_unix
    assert decoded['username'] == "test_user"


def test_verify_jwt_token_valid(mock_settings, mocker):
    mocker.patch.dict('os.environ', {'JWT_SECRET_KEY': 'mysecret'})

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105
    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )


    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    valid_token = jwt.encode({"exp": expiration, "username": "test_user"}, 'mysecret', algorithm='HS256')
    auth.token = valid_token

    assert auth.verify_jwt_token() is True

def test_verify_jwt_token_expired(mock_settings, mocker):
    mocker.patch.dict('os.environ', {'JWT_SECRET_KEY': 'mysecret'})

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105
    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )

    expiration = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    expired_token = jwt.encode({"exp": expiration, "username": "test_user"}, 'mysecret', algorithm='HS256')
    auth.token = expired_token

    assert auth.verify_jwt_token() is False

def test_verify_jwt_token_invalid(mock_settings, mocker):
    mocker.patch.dict('os.environ', {'JWT_SECRET_KEY': 'mysecret'})

    test_user = "test_user"
    test_pass = "test_pass"  # noqa: S105
    auth = SwiftAuthenticator(
        test_user,
        test_pass,
        mock_settings,
    )

    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    invalid_token = jwt.encode({"exp": expiration, "username": "test_user"}, 'wrongsecret', algorithm='HS256')
    auth.token = invalid_token

    assert auth.verify_jwt_token() is False