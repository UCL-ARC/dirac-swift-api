import os

pytest_plugins = [
    "tests.fixtures.test_http_requests",
    "tests.fixtures.test_output_files",
    "tests.fixtures.test_data",
]

os.environ["DB_URL"] = "http://a/test/url"
os.environ["JWT_SECRET_KEY"] = "a_test_secret_key"  # noqa: S105
