from api.main import app
from fastapi import status
from fastapi.testclient import TestClient

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ping": "pong"}
