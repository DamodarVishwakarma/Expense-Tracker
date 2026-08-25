from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.models.token import Token
from app.models.user import LoginRequest, UserCreate, UserInDB, UserPublic
from app.services.auth_service import authenticate_user
from app.services.user_service import create_user

router = APIRouter(tags=["auth"])


def public_user(user: UserInDB) -> UserPublic:
    return UserPublic(id=user.username, name=user.full_name, email=user.email)


def token_for(user: UserInDB) -> Token:
    return Token(
        access_token=create_access_token(user.username), user=public_user(user)
    )


@router.post("/api/auth/login", response_model=Token)
@router.post("/login", response_model=Token, include_in_schema=False)
def login(credentials: LoginRequest) -> Token:
    user = authenticate_user(credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_for(user)


@router.post(
    "/api/auth/token",
    response_model=Token,
    summary="OAuth2 login for Swagger UI",
    include_in_schema=False,
)
def oauth2_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authenticate an OAuth2 password form, treating `username` as an email."""
    user = authenticate_user(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_for(user)


@router.post(
    "/api/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED
)
@router.post(
    "/signup",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def signup(data: UserCreate) -> Token:
    user = create_user(data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    return token_for(user)
