import pytest

def test_signup(client):
    res = client.post("/api/v1/auth/signup", json={"email": "test@example.com", "password": "Password1!"})
    assert res.status_code == 201
    assert "id" in res.json()
    assert "password" not in res.json()

def test_signup_duplicate(client):
    client.post("/api/v1/auth/signup", json={"email": "test2@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/signup", json={"email": "test2@example.com", "password": "Password1!"})
    assert res.status_code == 409

def test_signup_weak_password(client):
    res = client.post("/api/v1/auth/signup", json={"email": "weak@example.com", "password": "weak"})
    assert res.status_code == 422

def test_login_success_and_me(client):
    client.post("/api/v1/auth/signup", json={"email": "login@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "login@example.com", "password": "Password1!"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    
    res2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    assert res2.json()["email"] == "login@example.com"

def test_login_failure(client):
    res = client.post("/api/v1/auth/login", data={"username": "wrong@example.com", "password": "wrong"})
    assert res.status_code == 401

def test_protected_endpoints_no_auth(client):
    res = client.post("/api/v1/centres/", json={"name": "No Auth", "city": "City", "address": "Addr"})
    assert res.status_code == 401
    
    res2 = client.post("/api/v1/tests/", json={"name": "No Auth Test"})
    assert res2.status_code == 401
