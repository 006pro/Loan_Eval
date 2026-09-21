from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUserOut, LoginRequest, RegisterRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.register_client(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.authenticate(db, payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> None:
    # Stateless JWT: the client discards its token. No server-side session exists.
    return None


@router.get("/me", response_model=CurrentUserOut)
def get_me(user: User = Depends(get_current_user)) -> CurrentUserOut:
    return auth_service.get_current_user_out(user)
