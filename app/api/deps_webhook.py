import hmac
import hashlib
from fastapi import Request, HTTPException, Header
from app.core.config import settings

async def verify_signature(request: Request, x_signature: str = Header(None)):
    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    body = await request.body()
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
