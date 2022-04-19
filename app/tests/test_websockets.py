from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from app import api
from app.api import app, websocket_endpoint

client = TestClient(app)


def test_websocket1():
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "Hello WebSocket"}