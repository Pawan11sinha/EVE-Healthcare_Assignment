from fastapi import FastAPI
from app.core.config import settings
from app.api.routers import health, centres, tests, auth, bookings, payments

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["health"])
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(bookings.router, prefix=f"{settings.API_V1_STR}/bookings", tags=["bookings"])
app.include_router(payments.router, prefix=f"{settings.API_V1_STR}/payments", tags=["payments"])
app.include_router(centres.router, prefix=f"{settings.API_V1_STR}/centres", tags=["centres"])
app.include_router(tests.router, prefix=f"{settings.API_V1_STR}/tests", tags=["tests"])
