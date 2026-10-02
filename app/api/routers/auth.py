from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.services.user import UserService
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.core.exceptions import AppException

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error (weak password, bad email)"},
    },
)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **email**: must be a valid email address
    - **password**: minimum 8 characters, at least one letter and one digit
    """
    return UserService.create_user(db, user_in)


@router.post(
    "/login",
    response_model=Token,
    summary="Obtain a JWT access token",
    responses={401: {"description": "Invalid credentials"}},
)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate with email + password; returns a Bearer token."""
    user = UserService.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AppException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", code="UNAUTHORIZED")

    access_token = create_access_token(subject=str(user.id))
    from app.core.config import settings
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the current authenticated user",
    responses={401: {"description": "Not authenticated"}},
)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently logged-in user."""
    return current_user
