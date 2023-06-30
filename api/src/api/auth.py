"""Module to handle authentiation against the database server."""
import json
from pathlib import Path

import requests
from fastapi import status
from loguru import logger
from requests import Session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from api.config import get_settings


class SwiftAuthenticator:
    """Class to handle authentication against the Virgo DB."""

    def __init__(
        self,
        cookies_file: Path = Path(__file__).parents[5] / "api/cookie_jar.txt",
    ):
        """Class constructor for authenticator object.

        Args:
            cookies_file (str, optional): Name of the cookie jar file.
                Defaults to "cookie_jar.txt".
        """
        settings = get_settings()

        self.username = settings.username
        self.password = settings.password.get_secret_value()
        self.db_url = settings.db_url
        logger.info(f"Settings cookies path as {cookies_file}")

        self.cookies_file = cookies_file

    def authenticate(self) -> bool:
        """Authenticate against the VirgoDB server.

        Returns:
            bool: Authentication successful if True, unsuccessful if False
        """
        session = Session()
        session = self.load_cookies(session)
        try:
            response = session.get(self.db_url, auth=(self.username, self.password))
            if response.status_code == status.HTTP_200_OK:
                self.save_cookies(session)
                return True
            return False
        except requests.exceptions.RequestException as exception:
            logger.error("Malformed URL in request.")
            logger.error(exception)
            return False

    def save_cookies(self, session: requests.Session) -> requests.Session:
        """Save cookies associated with a session object.

        Args:
            session (requests.session): Requests session object

        Returns:
            Session: Updated requests session object
        """
        with self.cookies_file.open("w") as cookies:
            json.dump(dict_from_cookiejar(session.cookies), cookies)
        return session

    def load_cookies(self, session: Session) -> Session:
        """Load cookies associated with a previous session, if they exist.

        Args:
            session (Session): Current session object

        Returns:
            Session: Session object updated with previously saved cookies
        """
        if self.cookies_file.exists():
            logger.info(
                f"Cookies from previous session found in {self.cookies_file}",
            )
            with self.cookies_file.open("r") as cookies:
                session.cookies.update(cookiejar_from_dict(json.load(cookies)))
        else:
            logger.info(
                "No previous session cookies found - creating new session cookies",
            )
        return session
