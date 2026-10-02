import sys
import os
import hmac
import hashlib
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings

def sign_payload(payload_dict):
    body = json.dumps(payload_dict, separators=(',', ':')).encode()
    signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return body, signature

if __name__ == "__main__":
    payload = {
        "event_id": "evt_test_123",
        "provider_reference": "SIM-TESTREF",
        "status": "SUCCESS",
        "amount": 1000.0
    }
    body, sig = sign_payload(payload)
    print(f"Payload: {body.decode()}")
    print(f"X-Signature: {sig}")
