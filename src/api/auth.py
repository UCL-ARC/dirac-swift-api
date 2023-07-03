"""Module to handle authentiation against the database server."""
import json
from pathlib import Path

import requests
from fastapi import status
from loguru import logger
from requests import Session
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

from api.config import Settings


class SwiftAuthenticator:
    """Class to handle authentication against the Virgo DB."""

    def __init__(
        self,
        settings: Settings,
        cookies_file: Path = Path(__file__).parents[5] / "src/api/cookie_jar.txt",
    ):
        """Class constructor for authenticator object.

        Args:
            cookies_file (str, optional): Name of the cookie jar file.
                Defaults to "cookie_jar.txt".
        """
        self.username = settings.username
        self.password = settings.password.get_secret_value()
        self.db_url = settings.db_url
        logger.info(f"Settings cookies path as {cookies_file}")

        self.cookies_file = cookies_file

    def validate_credentials(self, session: Session) -> int:
        """Validate user credentials.

        Return an appropriate status code to denote
        successful or unsuccessful auth

        Returns:
            int: Denotes status of authentication request
        """
        try:
            response = session.get(
                self.db_url,
                auth=(self.username, self.password),
                cookies=session.cookies,
            )
            if response.status_code == status.HTTP_200_OK:
                self.save_cookies(session)
            elif response.status_code == status.HTTP_401_UNAUTHORIZED:
                message = "Unauthorised user."
                logger.error(message)
            return response.status_code
        except requests.exceptions.RequestException as exception:
            logger.error("Malformed URL in request.")
            logger.error(exception)
            return status.HTTP_404_NOT_FOUND

    def authenticate(self) -> int:
        """Authenticate against the VirgoDB server.

        Returns:
            int: HTTP status code of authentication request
        """
        session = Session()
        session = self.load_cookies(session)
        return self.validate_credentials(session)

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
