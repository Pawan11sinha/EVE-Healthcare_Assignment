import pytest
from datetime import datetime, timedelta, timezone

@pytest.fixture
def payment_auth_headers(client):
    client.post("/api/v1/auth/signup", json={"email": "payment@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "payment@example.com", "password": "Password1!"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

@pytest.fixture
def other_user_headers(client):
    client.post("/api/v1/auth/signup", json={"email": "payment_other@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "payment_other@example.com", "password": "Password1!"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

def create_booking(client, auth_headers):
    c = client.post("/api/v1/centres/", json={"name": "P1", "city": "City", "address": "Addr"}, headers=auth_headers).json()
    t = client.post("/api/v1/tests/", json={"name": "T_Payment"}, headers=auth_headers).json()
    client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": 1000}, headers=auth_headers)
    
    future_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    res = client.post("/api/v1/bookings/", json={"centre_id": c['id'], "test_id": t['id'], "appointment_at": future_date}, headers=auth_headers)
    return res.json()

def test_payment_success(client, payment_auth_headers):
    booking = create_booking(client, payment_auth_headers)
    
    res = client.post("/api/v1/payments/", json={"booking_id": booking["id"], "force_outcome": "SUCCESS"}, headers=payment_auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["payment"]["status"] == "SUCCESS"
    assert data["booking_status"] == "CONFIRMED"
    
    res2 = client.post("/api/v1/payments/", json={"booking_id": booking["id"], "force_outcome": "SUCCESS"}, headers=payment_auth_headers)
    assert res2.status_code == 409

def test_payment_failure(client, payment_auth_headers):
    booking = create_booking(client, payment_auth_headers)
    
    res = client.post("/api/v1/payments/", json={"booking_id": booking["id"], "force_outcome": "FAILED"}, headers=payment_auth_headers)
    assert res.status_code == 200
    assert res.json()["payment"]["status"] == "FAILED"
    assert res.json()["booking_status"] == "FAILED"

def test_payment_wrong_user(client, payment_auth_headers, other_user_headers):
    booking = create_booking(client, payment_auth_headers)
    
    res = client.post("/api/v1/payments/", json={"booking_id": booking["id"], "force_outcome": "SUCCESS"}, headers=other_user_headers)
    assert res.status_code == 404

def test_payment_bad_booking(client, payment_auth_headers):
    res = client.post("/api/v1/payments/", json={"booking_id": "00000000-0000-0000-0000-000000000000", "force_outcome": "SUCCESS"}, headers=payment_auth_headers)
    assert res.status_code == 404

def test_get_payment(client, payment_auth_headers, other_user_headers):
    booking = create_booking(client, payment_auth_headers)
    res = client.post("/api/v1/payments/", json={"booking_id": booking["id"], "force_outcome": "SUCCESS"}, headers=payment_auth_headers)
    payment_id = res.json()["payment"]["id"]
    
    res2 = client.get(f"/api/v1/payments/{payment_id}", headers=payment_auth_headers)
    assert res2.status_code == 200
    assert res2.json()["id"] == payment_id
    
    res3 = client.get(f"/api/v1/payments/{payment_id}", headers=other_user_headers)
    assert res3.status_code == 404
