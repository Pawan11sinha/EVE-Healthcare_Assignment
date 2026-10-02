from typing import Generator
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.config import settings
from app.core.exceptions import AppException
import jwt
from pydantic import ValidationError
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            code="UNAUTHORIZED"
        )
    user = db.query(User).filter(str(User.id) == token_data.sub).first()
    if not user:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            code="UNAUTHORIZED"
        )
    return user
