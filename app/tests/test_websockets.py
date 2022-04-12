from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from app import api
from app.api import app, websocket_endpoint

client = TestClient(app)


def test_websocket():
    with client.websocket_connect('https://api.treffen.fr/ws/chat/private/28254b60-fd7b-4948-974d-bc78578a6068/35b0bee8'
                                  '-38c4-4abd-ba2f-23f5e47c9566') as websocket:
        websocket.receive_text("Mon message")
        assert 0


def test_websocket1():
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data == {"msg": "Hello WebSocket"}