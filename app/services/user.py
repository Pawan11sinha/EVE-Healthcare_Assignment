from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.core.exceptions import AppException
from typing import Optional

class UserService:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        user = UserService.get_user_by_email(db, user_in.email)
        if user:
            raise AppException(status_code=409, detail="Email already registered", code="EMAIL_EXISTS")
        
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise AppException(status_code=409, detail="Email already registered", code="EMAIL_EXISTS")
