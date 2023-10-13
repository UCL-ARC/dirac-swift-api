import dotenv

pytest_plugins = [
    "tests.fixtures.test_http_requests",
    "tests.fixtures.test_output_files",
    "tests.fixtures.test_data",
]


def pytest_configure():
    dotenv.load_dotenv("tests/data/.env.test")
