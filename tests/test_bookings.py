import pytest
from datetime import datetime, timedelta, timezone

@pytest.fixture
def user2_auth_headers(client):
    client.post("/api/v1/auth/signup", json={"email": "user2@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "user2@example.com", "password": "Password1!"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def test_create_and_get_booking(client, auth_headers, user2_auth_headers):
    c = client.post("/api/v1/centres/", json={"name": "B1", "city": "City", "address": "Addr"}, headers=auth_headers).json()
    t = client.post("/api/v1/tests/", json={"name": "TBooking"}, headers=auth_headers).json()
    client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": 500}, headers=auth_headers)
    
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    
    res = client.post("/api/v1/bookings/", json={"centre_id": c['id'], "test_id": t['id'], "appointment_at": future_date}, headers=auth_headers)
    assert res.status_code == 200
    booking = res.json()
    assert booking["status"] == "PENDING"
    assert booking["amount"] == "500.0"
    
    res2 = client.get("/api/v1/bookings/", headers=auth_headers)
    assert len(res2.json()) >= 1
    
    res3 = client.get(f"/api/v1/bookings/{booking['id']}", headers=auth_headers)
    assert res3.status_code == 200
    
    res4 = client.get(f"/api/v1/bookings/{booking['id']}", headers=user2_auth_headers)
    assert res4.status_code == 404
    
    res5 = client.get("/api/v1/bookings/not-a-uuid", headers=auth_headers)
    assert res5.status_code == 404

def test_cancel_booking(client, auth_headers):
    c = client.post("/api/v1/centres/", json={"name": "B2", "city": "City", "address": "Addr"}, headers=auth_headers).json()
    t = client.post("/api/v1/tests/", json={"name": "TBooking2"}, headers=auth_headers).json()
    client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": 500}, headers=auth_headers)
    
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    booking = client.post("/api/v1/bookings/", json={"centre_id": c['id'], "test_id": t['id'], "appointment_at": future_date}, headers=auth_headers).json()
    
    res = client.post(f"/api/v1/bookings/{booking['id']}/cancel", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "CANCELLED"
    
    res2 = client.post(f"/api/v1/bookings/{booking['id']}/cancel", headers=auth_headers)
    assert res2.status_code == 409
