import pytest

@pytest.fixture
def auth_headers(client):
    client.post("/api/v1/auth/signup", json={"email": "admin@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "Password1!"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_create_centre(client, auth_headers):
    response = client.post("/api/v1/centres/", json={"name": "C1", "city": "City", "address": "Addr"}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "C1"

def test_get_centres(client, auth_headers):
    client.post("/api/v1/centres/", json={"name": "C2", "city": "Delhi", "address": "Addr"}, headers=auth_headers)
    response = client.get("/api/v1/centres/?city=Delhi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[-1]["city"] == "Delhi"

def test_add_test_to_centre(client, auth_headers):
    c = client.post("/api/v1/centres/", json={"name": "C3", "city": "City", "address": "Addr"}, headers=auth_headers).json()
    t = client.post("/api/v1/tests/", json={"name": "T1"}, headers=auth_headers).json()
    
    # Happy path
    res = client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": 100.50}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["price"] == "100.5"
    
    # 409 Conflict
    res2 = client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": 150.00}, headers=auth_headers)
    assert res2.status_code == 409
    
    # 404 Centre not found
    res3 = client.post(f"/api/v1/centres/999/tests", json={"test_id": t["id"], "price": 150.00}, headers=auth_headers)
    assert res3.status_code == 404
    
    # Validation error (price <= 0)
    res4 = client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": -10}, headers=auth_headers)
    assert res4.status_code == 422
    
def test_get_centre_details(client, auth_headers):
    c = client.post("/api/v1/centres/", json={"name": "C4", "city": "City", "address": "Addr"}, headers=auth_headers).json()
    t = client.post("/api/v1/tests/", json={"name": "T2"}, headers=auth_headers).json()
    client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": 200}, headers=auth_headers)
    
    res = client.get(f"/api/v1/centres/{c['id']}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["centre_tests"]) == 1
    assert data["centre_tests"][0]["price"] == "200.0"
