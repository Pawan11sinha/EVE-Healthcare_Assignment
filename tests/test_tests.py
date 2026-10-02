import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/api/v1/auth/signup", json={"email": "admin2@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "admin2@example.com", "password": "Password1!"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_create_test(client, auth_headers):
    response = client.post("/api/v1/tests/", json={"name": "Blood Test"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Blood Test"
    
def test_create_test_duplicate(client, auth_headers):
    client.post("/api/v1/tests/", json={"name": "Unique Test"}, headers=auth_headers)
    response = client.post("/api/v1/tests/", json={"name": "Unique Test"}, headers=auth_headers)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "TEST_EXISTS"
