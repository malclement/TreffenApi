from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_user_info_by_id():
    response = client.get("https://api.treffen.fr/user/info/id/35b0bee8-38c4-4abd-ba2f-23f5e47c9566")
    assert response.status_code == 200
    assert response.json() == {"_id": {"$oid": "6230a2dcb0487d13aae06c41"},
                               "id": "35b0bee8-38c4-4abd-ba2f-23f5e47c9566",
                               "surname": "Clément",
                               "fullname": "Malige",
                               "email": "clement@x.com",
                               "password": "weakpassword"}


def test_user_info_by_id_wrong_id():
    response = client.get("https://api.treffen.fr/user/info/id/35b1bee8-38c4-4abd-ba2f-23f5e47c9566")
    assert response.status_code == 404
    assert response.json() == {"detail": "No id Found"}
