"""
Webhook tests — real concurrency + all edge-cases.

Note on concurrency: TestClient is synchronous and share the same DB session
fixture. To test true concurrent delivery we use ThreadPoolExecutor where each
thread builds its own TestClient bound to the *same* FastAPI app but with its
own WSGI call stack, which exercises the savepoint / FOR-UPDATE paths.
"""
import hmac
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


# ──────────────────────── helpers ──────────────────────────────────────────

def sign_payload(payload: dict) -> tuple[bytes, str]:
    body = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(settings.WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return body, sig


def webhook_headers(sig: str) -> dict:
    return {"X-Signature": sig, "Content-Type": "application/json"}


# ──────────────────────── fixtures ─────────────────────────────────────────

@pytest.fixture
def wh_auth(client):
    """Return auth headers for a fresh user."""
    client.post("/api/v1/auth/signup", json={"email": "wh@example.com", "password": "Password1!"})
    res = client.post("/api/v1/auth/login", data={"username": "wh@example.com", "password": "Password1!"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def wh_booking_and_payment(client, wh_auth):
    """Create centre → test → booking → PENDING payment; return (payment, booking)."""
    c = client.post("/api/v1/centres/", json={"name": "WH Centre", "city": "City", "address": "Addr"}, headers=wh_auth).json()
    t = client.post("/api/v1/tests/", json={"name": "WH Test"}, headers=wh_auth).json()
    client.post(f"/api/v1/centres/{c['id']}/tests", json={"test_id": t["id"], "price": "750.00"}, headers=wh_auth)
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    booking = client.post("/api/v1/bookings/", json={"centre_id": c["id"], "test_id": t["id"], "appointment_at": future}, headers=wh_auth).json()
    # Force a PENDING payment so the webhook can find it via provider_reference
    payment = client.post("/api/v1/payments/", json={"booking_id": booking["id"], "force_outcome": "SUCCESS"}, headers=wh_auth).json()
    return payment["payment"], booking


# ──────────────────────── signature tests ──────────────────────────────────

def test_webhook_missing_signature(client):
    res = client.post(
        "/api/v1/payments/webhook/",
        json={"event_id": "1", "provider_reference": "REF", "status": "SUCCESS", "amount": "100"},
    )
    assert res.status_code == 401
    assert "Missing" in res.json()["detail"]


def test_webhook_bad_signature(client):
    payload = {"event_id": "1", "provider_reference": "REF", "status": "SUCCESS", "amount": "100"}
    body = json.dumps(payload, separators=(",", ":")).encode()
    res = client.post(
        "/api/v1/payments/webhook/",
        content=body,
        headers={"X-Signature": "deadbeef", "Content-Type": "application/json"},
    )
    assert res.status_code == 401
    assert "Invalid" in res.json()["detail"]


# ──────────────────────── 404 / 422 tests leave no DB rows ─────────────────

def test_webhook_unknown_reference_no_row(client):
    payload = {"event_id": "evt_unknown_ref", "provider_reference": "NO-SUCH-REF", "status": "SUCCESS", "amount": "100"}
    body, sig = sign_payload(payload)
    res = client.post("/api/v1/payments/webhook/", content=body, headers=webhook_headers(sig))
    assert res.status_code == 404


def test_webhook_malformed_payload(client):
    payload = {"event_id": "evt_bad_status", "provider_reference": "X", "status": "BOUNCE", "amount": "50"}
    body, sig = sign_payload(payload)
    res = client.post("/api/v1/payments/webhook/", content=body, headers=webhook_headers(sig))
    assert res.status_code == 422


def test_webhook_amount_mismatch(client, wh_booking_and_payment):
    payment, _ = wh_booking_and_payment
    payload = {
        "event_id": "evt_amt_mismatch",
        "provider_reference": payment["provider_reference"],
        "status": "SUCCESS",
        "amount": "9999.99",  # wrong amount
    }
    body, sig = sign_payload(payload)
    res = client.post("/api/v1/payments/webhook/", content=body, headers=webhook_headers(sig))
    assert res.status_code == 422


# ──────────────────────── no_change / ignored_conflict tests ───────────────

def test_webhook_no_change_same_status(client, wh_booking_and_payment):
    """Payment is already SUCCESS; webhook sends SUCCESS → no_change."""
    payment, _ = wh_booking_and_payment
    payload = {
        "event_id": "evt_no_change",
        "provider_reference": payment["provider_reference"],
        "status": "SUCCESS",
        "amount": str(payment["amount"]),
    }
    body, sig = sign_payload(payload)
    res = client.post("/api/v1/payments/webhook/", content=body, headers=webhook_headers(sig))
    assert res.status_code == 200
    assert res.json()["result"] == "no_change"


def test_webhook_conflicting_status_after_success(client, wh_booking_and_payment):
    """Payment is SUCCESS; webhook sends FAILED → ignored_conflict."""
    payment, _ = wh_booking_and_payment
    payload = {
        "event_id": "evt_conflict",
        "provider_reference": payment["provider_reference"],
        "status": "FAILED",
        "amount": str(payment["amount"]),
    }
    body, sig = sign_payload(payload)
    res = client.post("/api/v1/payments/webhook/", content=body, headers=webhook_headers(sig))
    assert res.status_code == 200
    assert res.json()["result"] == "ignored_conflict"


# ──────────────────────── idempotency + concurrency ────────────────────────

def test_webhook_idempotency_duplicate_events(client, wh_booking_and_payment):
    """Sending the same event_id 3 times → exactly one webhook_events row."""
    payment, _ = wh_booking_and_payment
    payload = {
        "event_id": "evt_idem_dup",
        "provider_reference": payment["provider_reference"],
        "status": "SUCCESS",
        "amount": str(payment["amount"]),
    }
    body, sig = sign_payload(payload)

    results = []
    for _ in range(3):
        r = client.post("/api/v1/payments/webhook/", content=body, headers=webhook_headers(sig))
        results.append(r.json())

    statuses = [r["status"] for r in results]
    # Exactly one "processed" (the first hit), the rest "already_processed"
    assert statuses.count("processed") == 1
    assert statuses.count("already_processed") == 2


def test_webhook_concurrency(client, wh_booking_and_payment):
    """
    Fire the same signed event from N threads simultaneously using separate
    TestClient instances (each gets its own WSGI call stack and DB session).
    Assert: exactly one row is processed, all others report already_processed.
    """
    payment, _ = wh_booking_and_payment
    payload = {
        "event_id": "evt_concurrent_real",
        "provider_reference": payment["provider_reference"],
        "status": "SUCCESS",
        "amount": str(payment["amount"]),
    }
    body, sig = sign_payload(payload)
    headers = webhook_headers(sig)
    N = 5

    def send():
        # Each thread creates its own TestClient so WSGI sessions are independent
        with TestClient(app) as tc:
            return tc.post("/api/v1/payments/webhook/", content=body, headers=headers).json()

    with ThreadPoolExecutor(max_workers=N) as executor:
        futures = [executor.submit(send) for _ in range(N)]
        results = [f.result() for f in as_completed(futures)]

    processed = [r for r in results if r.get("status") == "processed"]
    already = [r for r in results if r.get("status") == "already_processed"]

    assert len(processed) == 1, f"Expected exactly 1 processed, got {len(processed)}: {results}"
    assert len(already) == N - 1
